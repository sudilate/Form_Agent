import asyncio
from stt_utils import recognize_speech
from form_utils import extract_form_fields
from agent_runner import run_agent

FORM_URL = "https://main.d3tmximhpifgea.amplifyapp.com/signup"

async def main():
    print("[INFO] Extracting form fields...")
    fields = extract_form_fields(FORM_URL)

    form_data = {}
    for field in fields:
        print(f"[PROMPT] Please say the value for: {field}")
        spoken_value = recognize_speech()
        print(f"[RECEIVED] {field}: {spoken_value}")
        form_data[field] = spoken_value

    task = f"Fill the form at {FORM_URL} using the following data:\n{form_data} and get only relevant information to fill the form and use that information to fill the form"
    print("[INFO] Running agent to fill the form...")
    result = await run_agent(task)
    print("\n✅ Final Result:\n", result)

if __name__ == "__main__":
    asyncio.run(main())
