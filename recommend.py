import os
import json

from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores import FAISS
import firebase_admin
import streamlit as st
import tiktoken
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_core.documents import Document
from pydantic import BaseModel, ValidationError
from firebase_admin import credentials, firestore
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from firebase_admin.exceptions import FirebaseError

load_dotenv()
# Initialize Firebase
cred = credentials.Certificate("minsdk-nweuu-4b3524132f.json")  # Replace with your service account key
# Initialize Firebase (ensure this is done only once)
if not firebase_admin._apps:
    firebase_app = firebase_admin.initialize_app(cred)
db = firestore.client()


# Define a Pydantic model for user input validation
class UserInput(BaseModel):
    cv: str


# Fetch all data from Firebase
@st.cache_data
def load_data_from_db():
    try:
        universities_ref = db.collection('universities')
        university_with_courses = {}

        for university_doc in universities_ref.stream():
            university_data = university_doc.to_dict()
            university_name = university_data['name']

            courses_ref = university_doc.reference.collection('courses')
            courses = []
            for course_doc in courses_ref.stream():
                course_data = course_doc.to_dict()
                courses.append(course_data)

            university_with_courses[university_name] = courses

        return university_with_courses
    except FirebaseError as e:
        print("FirebaseError:", e)  # Debug statement
        return None


def generate_documents(universities_and_courses):
    documents = []
    texts_to_embed = []

    for university, courses in universities_and_courses.items():
        for course in courses:
            course_name = course['name']
            level = course['level']
            text_to_embed = f"{university} {course_name} {level}"
            texts_to_embed.append(text_to_embed)
            documents.append({
                "prompt": text_to_embed,
                "metadata": {'school': university, 'course': course_name, 'level': level}
            })

    return documents, texts_to_embed


def create_vector_db(documents, texts_to_embed, file_path="faiss_index"):
    instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
    vectordb = FAISS.from_texts(texts=texts_to_embed, embedding=instructor_embeddings,
                                metadatas=[doc['metadata'] for doc in documents])

    vectordb.save_local(file_path)
    print('DONE')


# Translate and recommend courses
def recommend_courses_from_vector(cv_text):
    # Initialize the instructor embeddings
    instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")

    # Load the vector database
    vectordb = FAISS.load_local('faiss_index', instructor_embeddings, allow_dangerous_deserialization=True)

    # Create a retriever for querying the vector database
    retriever = vectordb.as_retriever(score_threshold=0.7)

    # Retrieve relevant documents based on the CV text
    retrieved_docs = retriever.get_relevant_documents(cv_text)

    # Format the retrieved data for the prompt
    universities_and_courses = "\n".join(
        [f"{doc.metadata['school']}: {doc.metadata['course']} ({doc.metadata['level']})" for doc in retrieved_docs]
    )

    # Define the prompt template
    prompt_template = """
    Based on the following CV or experience provided by the user:
    {question}

    Recommend universities and their courses that match or are closely related to the user's interests and qualifications specified in their CV from the following list of universities and courses:
    {context}

    If a perfect match is not found, recommend courses that are related or in a similar field. Avoid recommending unrelated courses.

    Please provide the recommendations in the following format:
    {{
        "recommendations": [
            {{
                "school": "<University name>",
                "courses": [
                    {{"name": "<Course name>", "level": "<'Master's' or 'PhD'>"}},
                    ...
                ]
            }},
            ...
        ]
    }}
    """

    # Format the prompt with the CV and retrieved universities and courses data
    prompt_text = prompt_template.format(question=cv_text, context=universities_and_courses)

    # Initialize the language model
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", google_api_key=os.environ.get('GEMINI_API_KEY')
    )

    # Define the prompt for the LLM chain
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=prompt_template
    )
    # Create the RetrievalQA chain
    chain = RetrievalQA.from_chain_type(llm=llm,
                                        chain_type="stuff",
                                        retriever=retriever,
                                        input_key="query",
                                        return_source_documents=True,
                                        chain_type_kwargs={"prompt": prompt})

    # Run the chain and get the response
    resp = chain({"query": cv_text, "universities_and_courses": universities_and_courses})

    # Tokenize the prompt text and count tokens
    tokenizer = tiktoken.get_encoding("p50k_base")
    tokens = tokenizer.encode(prompt_text)
    token_count = len(tokens)

    # Print token count
    print(f"Token count: {token_count}")

    return resp


# Streamlit app
def main():
    st.title("University and Course Recommendation")
    st.write("Please enter your CV or experience details to get recommendations for universities and courses.")

    cv_input = st.text_area("Enter the field you are interested in")

    if st.button("Get Recommendations"):
        try:
            # Validate user input
            user_input = UserInput(cv=cv_input)

            # Get recommendations
            recommendations = recommend_courses_from_vector(user_input.cv)
            # Parse and display recommendations
            try:
                recommendations_json = json.loads(recommendations.get('result'))
                for rec in recommendations_json["recommendations"]:
                    st.write(f"**University:** {rec['school']}")
                    st.write("**Courses:**")
                    for course in rec["courses"]:
                        st.write(f"- {course['name']} ({course['level']})")
            except json.JSONDecodeError as e:
                st.write("No relevant courses found.")
                print(str(e))

        except ValidationError as e:
            st.write(f"Input Error: {e}")


if __name__ == "__main__":
    main()

