import os
import time
from enum import Enum
from typing import Optional

from dotenv import load_dotenv
from firebase_admin.exceptions import FirebaseError
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, WebDriverException
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()
# Initialize Firebase Admin SDK with your service account key
cred = credentials.Certificate("minsdk-nweuu-4b3524132f.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def scrape() -> list:
    # Initialize WebDriver using Firefox
    driver = webdriver.Chrome()
    try:
        # Navigate to the webpage
        driver.get("https://www.gcub.org.br/bsp/application-form.php")

        # Click the button to proceed to the next step
        next_step_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button#passo005"))
        )
        next_step_button.click()

        # Initialize list to store scraped data
        schools_and_courses = list()

        # Wait for the university select element to be available
        university_select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select#universidade001"))
        )

        # Get all university options
        university_select = Select(university_select_element)
        university_options = university_select.options

        # Loop through each university option
        for university_option in university_options[1:]:
            school_name = university_option.text.strip()

            # Retry loop for selecting university and getting courses
            for _ in range(10):  # Retry up to 3 times
                try:
                    university_select.select_by_visible_text(university_option.text)
                    time.sleep(1)  # Add a small delay to stabilize the page

                    # Wait for the program select element to be available
                    program_select_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "select#programa001"))
                    )

                    # Get all program options
                    program_select = Select(program_select_element)
                    program_options = program_select.options

                    # Initialize list to store courses
                    courses = []

                    # Loop through each program option
                    for program_option in program_options[1:]:
                        courses.append(program_option.text.strip())

                    if courses:
                        # Build dictionary for each selection
                        data = {
                            'school': school_name,
                            'courses': courses
                        }

                        schools_and_courses.append(data)
                        print(data)

                        break  # Break out of retry loop if successful
                    print(f"{school_name} couldn't select courses, retrying....")

                except (StaleElementReferenceException, TimeoutException) as e:
                    print(f"Exception occurred: {str(e)}")
                    print(f"Retrying selection of {school_name}")
                    continue

            else:
                print(f"Failed to scrape data for {school_name} after retries")

    finally:
        driver.quit()

    return schools_and_courses


class ProgramEnum(Enum):
    mtech = "Master's"
    phd = 'PhD'


class CourseType(BaseModel):
    title: str
    level: ProgramEnum


class School(BaseModel):
    school: str
    courses: Optional[list[CourseType]]


def translate(data):
    # Define the template
    output_parser = PydanticOutputParser(pydantic_object=School)
    format_instructions = output_parser.get_format_instructions()
    template = PromptTemplate(
        input_variables=["universities_and_courses", "format_instructions"],
        template="""
        Translate the following universities and their courses into English. Specify whether each course is a 
        Master's or a PhD program. Ensure all school names and their courses are translated completely:

        Universities and Courses:
        {universities_and_courses}

        Instructions:
        {format_instructions}

        Ensure all keys and values are enclosed in double quotes. Translate every university and course listed
        without skipping any. If the input is too long, continue until all content is translated. Ensure the 
        entire input is fully translated to English language.
        """

    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-pro", google_api_key=os.environ.get('GEMINI_API_KEY')
    )
    output = list()
    for entry in data:
        prompt_text = template.format(universities_and_courses=entry,
                                      format_instructions=format_instructions)
        # if entry.get('school')
        response = llm.invoke(prompt_text)
        school = output_parser.parse(response.content)
        print(school)
        output.append(school)
    return output


def save_to_firebase(data):
    for entry in data:
        # Create a new document in the 'universities' collection
        university_ref = db.collection('university').document()
        university_ref.set({
            'name': entry.school
        })

        # Get the university document ID
        university_id = university_ref.id

        # Loop through courses and add them to the 'courses' collection
        for course in entry.courses:
            db.collection('university').document(university_id).collection('courses').add({
                'name': course.title,
                'level': course.level.value
            })


if __name__ == "__main__":
    try:
        scraped_data = scrape()
        translated_data = translate(scraped_data)
        save_to_firebase(translated_data)
        print("Data saved to Firebase successfully.")
    except WebDriverException:
        print('Site Down')
    except OutputParserException as e:
        print(f'OutputParserException: {e}')
    except FirebaseError as e:
        print(f'FirebaseError: {e}')
    except Exception as e:
        print(f'Unexpected Exception: {e}')
