# form_engine.py

form_data = {
    "first_name": None,
    "email": None,
    "phone": None,
    "years_of_experience": None,
}

def update_form(entities: dict):
    for key, value in entities.items():
        if value and not form_data.get(key):
            form_data[key] = value

def get_next_question() -> str:
    if not form_data["first_name"]:
        return "What is your name?"
    if not form_data["email"]:
        return "What is your email?"
    if not form_data["phone"]:
        return "What is your phone number?"
    if not form_data["years_of_experience"]:
        return "How many years of experience do you have?"
    return None

def is_form_complete() -> bool:
    return all(value is not None for value in form_data.values())

def print_form():
    print("\n📄 Form Progress:")
    for k, v in form_data.items():
        print(f"{k}: {v}")
