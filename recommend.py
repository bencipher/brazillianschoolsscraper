import json

import tiktoken
import streamlit as st
from pydantic import BaseModel, ValidationError
from langchain_core.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores import FAISS

from configs.env_config import EnvironmentConfig
from configs.firebase import FirebaseService
from configs.google_generative_ai import GoogleGenerativeAIService
from llm_prompts import retrieve_prompt
from models import UserInput

# Load environment variables
env_config = EnvironmentConfig(".env")

# Initialize Firebase service
firebase_service = FirebaseService("minsdk-nweuu-4b3524132f.json")  # Replace with your service account key path


# Fetch all data from Firebase
@st.cache_data
def load_data_from_db():
    try:
        db = firebase_service.get_firestore_client()
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
    except Exception as e:
        print("Error:", e)  # Debug statement
        return None


# Generate documents for vector database
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


# Create vector database with FAISS
def create_vector_db(documents, texts_to_embed, file_path="faiss_index"):
    service = GoogleGenerativeAIService(env_config)
    huggingface_embeddings = service.get_huggingface_embeddings()

    vectordb = FAISS.from_texts(texts=texts_to_embed, embedding=huggingface_embeddings,
                                metadatas=[doc['metadata'] for doc in documents])
    vectordb.save_local(file_path)
    print('DONE')


# Recommend courses based on CV using vector database
def recommend_courses_from_vector(cv_text, llm_service):
    # Load HuggingFace embeddings
    service = GoogleGenerativeAIService(env_config)
    huggingface_embeddings = service.get_huggingface_embeddings()

    # Load the vector database
    vectordb = FAISS.load_local('faiss_index', huggingface_embeddings, allow_dangerous_deserialization=True)

    # Create a retriever for querying the vector database
    retriever = vectordb.as_retriever(score_threshold=0.7)

    # Retrieve relevant documents based on the CV text
    retrieved_docs = retriever.invoke(cv_text)
    print(retrieved_docs)
    # Format the retrieved data for the prompt
    universities_and_courses = "\n".join(
        [f"{doc.metadata['school']}: {doc.metadata['course']} ({doc.metadata['level']})" for doc in retrieved_docs]
    )

    # Define the prompt template

    prompt_text = retrieve_prompt.format(question=cv_text, context=universities_and_courses)

    # Get LLM instance from the service
    llm_instance = llm_service.get_llm_instance()

    # Define the prompt for the LLM chain
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=retrieve_prompt
    )

    # Create the RetrievalQA chain
    chain = RetrievalQA.from_chain_type(llm=llm_instance,
                                        chain_type="stuff",
                                        retriever=retriever,
                                        input_key="query",
                                        return_source_documents=True,
                                        chain_type_kwargs={"prompt": prompt})

    # Run the chain and get the response
    resp = chain({"query": cv_text, "universities_and_courses": universities_and_courses})

    # Print token count (assuming `tiktoken` usage)
    tokenizer = tiktoken.get_encoding("p50k_base")
    tokens = tokenizer.encode(prompt_text)
    token_count = len(tokens)
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

            # Initialize LLM service
            llm_service = GoogleGenerativeAIService(env_config)

            # Get recommendations
            recommendations = recommend_courses_from_vector(user_input.cv, llm_service)

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
