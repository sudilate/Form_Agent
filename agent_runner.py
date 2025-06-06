from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent  # Make sure this class can handle form automation
import os
from dotenv import load_dotenv

load_dotenv()
llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp',
    api_key=os.getenv("GEMINI_API_KEY")
)

async def run_agent(task_prompt: str):
    agent = Agent(task=task_prompt, llm=llm)
    result = await agent.run()
    return result.final_result()
