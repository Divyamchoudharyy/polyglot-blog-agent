import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


class GroqLLM:
    def __init__(self, model: str = "openai/gpt-oss-120b"):
        load_dotenv()
        self.model = model

    def get_llm(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set. Add it to your .env file.")
        try:
            return ChatGroq(api_key=api_key, model=self.model)
        except Exception as e:
            raise ValueError(f"Could not create Groq LLM: {e}") from e
