retrieve_prompt = """
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
