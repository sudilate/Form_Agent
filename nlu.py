# nlu.py

import re

def extract_entities(text):
    text = text.lower()
    entities = {}

    # First name
    match = re.search(r"my name is (\w+)", text)
    if match:
        entities["first_name"] = match.group(1)

    # Full name fallback
    match = re.search(r"i am (\w+)", text)
    if match and "first_name" not in entities:
        entities["first_name"] = match.group(1)

    # Email
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    if match:
        entities["email"] = match.group(0)

    # Phone number (Indian format)
    match = re.search(r"\b\d{10}\b", text)
    if match:
        entities["phone"] = match.group(0)

    # Years of experience
    match = re.search(r"(\d+)\s+(year|years)\s+(of)?\s*(experience)?", text)
    if match:
        entities["years_of_experience"] = int(match.group(1))

    # You can add more patterns here...

    return entities
