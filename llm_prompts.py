retrieve_prompt = """
Based on the following CV or experience provided by the user:
{question}

1. Identify and list all distinct academic fields or career opportunities mentioned in the input.

2. For each field or opportunity, recommend universities and their courses that match or are closely related to the user's interests and qualifications specified in their CV from the following list of universities and courses:
{context}

If a perfect match is not found, recommend courses that are related or in a similar field. Avoid recommending unrelated courses.

Please ensure all recommendations are translated to English before returning.

Response Format:
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

Example 1:

Input: "I have experience in cyber security, AI, and cloud computing."

Output: 
{{
    "recommendations": [
        {{
            "school": "University A",
            "courses": [
                {{"name": "Cyber Security Master's", "level": "Master's"}},
                {{"name": "Information Security PhD", "level": "PhD"}}
            ]
        }},
        {{
            "school": "University B",
            "courses": [
                {{"name": "Artificial Intelligence Master's", "level": "Master's"}},
                {{"name": "Machine Learning PhD", "level": "PhD"}}
            ]
        }},
        {{
            "school": "University C",
            "courses": [
                {{"name": "Cloud Computing Master's", "level": "Master's"}},
                {{"name": "Cloud Infrastructure PhD", "level": "PhD"}}
            ]
        }}
    ]
}}

Example 2:

Input: "With a background in data science, machine learning, and bioinformatics."

Output: 
{{
    "recommendations": [
        {{
            "school": "University D",
            "courses": [
                {{"name": "Data Science Master's", "level": "Master's"}},
                {{"name": "Data Analytics PhD", "level": "PhD"}}
            ]
        }},
        {{
            "school": "University E",
            "courses": [
                {{"name": "Machine Learning Master's", "level": "Master's"}},
                {{"name": "Artificial Intelligence PhD", "level": "PhD"}}
            ]
        }},
        {{
            "school": "University F",
            "courses": [
                {{"name": "Bioinformatics Master's", "level": "Master's"}},
                {{"name": "Computational Biology PhD", "level": "PhD"}}
            ]
        }}
    ]
}}

Example 3:

Input: "I have studied environmental science, renewable energy, and sustainable agriculture."

Output: 
{{
    "recommendations": [
        {{
            "school": "University G",
            "courses": [
                {{"name": "Environmental Science Master's", "level": "Master's"}},
                {{"name": "Environmental Studies PhD", "level": "PhD"}}
            ]
        }},
        {{
            "school": "University H",
            "courses": [
                {{"name": "Renewable Energy Master's", "level": "Master's"}},
                {{"name": "Sustainable Energy PhD", "level": "PhD"}}
            ]
        }},
        {{
            "school": "University I",
            "courses": [
                {{"name": "Sustainable Agriculture Master's", "level": "Master's"}},
                {{"name": "Agricultural Sustainability PhD", "level": "PhD"}}
            ]
        }}
    ]
}}

Example 4:

Input: "Experience in mechanical engineering, automotive design, and robotics."

Output: 
{{
    "recommendations": [
        {{
            "school": "University J",
            "courses": [
                {{"name": "Mechanical Engineering Master's", "level": "Master's"}},
                {{"name": "Engineering Mechanics PhD", "level": "PhD"}}
            ]
        }},
        {{
            "school": "University K",
            "courses": [
                {{"name": "Automotive Engineering Master's", "level": "Master's"}},
                {{"name": "Vehicle Design PhD", "level": "PhD"}}
            ]
        }},
        {{
            "school": "University L",
            "courses": [
                {{"name": "Robotics Master's", "level": "Master's"}},
                {{"name": "Robotic Systems PhD", "level": "PhD"}}
            ]
        }}
    ]
}}

Example 5:

Input: "Studied finance, business administration, and international trade."

Output: 
{{
    "recommendations": [
        {{
            "school": "University M",
            "courses": [
                {{"name": "Finance Master's", "level": "Master's"}},
                {{"name": "Financial Economics PhD", "level": "PhD"}}
            ]
        }},
        {{
            "school": "University N",
            "courses": [
                {{"name": "Business Administration Master's", "level": "Master's"}},
                {{"name": "Management PhD", "level": "PhD"}}
            ]
        }},
        {{
            "school": "University O",
            "courses": [
                {{"name": "International Trade Master's", "level": "Master's"}},
                {{"name": "Global Business PhD", "level": "PhD"}}
            ]
        }}
    ]
}}

Ensure the response is a valid JSON object with no extra markings or text added:
"""

load_prompt = """
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
