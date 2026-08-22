from google import genai
from google.genai import types, errors

from src.config.settings import get_api_key

# System prompt
SYSTEM_INSTRUCTION = (
    "You are a helpful and intelligent chatbot assistant. "
    "Analyze the WhatsApp chat history and generate ONLY the next reply. "
    "Do not include timestamps, sender names, or extra explanation."
)


class GeminiReplyGenerator:
    """
    Generates AI replies using Google's Gemini API.
    """

    def __init__(self, model_name: str = "gemini-3.6-flash") -> None:
        self.client = genai.Client(api_key=get_api_key())
        self.model_name = model_name

    def generate_reply(self, chat_history: str) -> str:
        """
        Generate a reply from chat history.
        """
        if not chat_history.strip():
            raise ValueError("Chat history cannot be empty.")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=chat_history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.7,
                ),
            )

            if response.text:
                return response.text.strip()

            raise RuntimeError("Gemini returned an empty response.")

        except errors.APIError as e:
            raise RuntimeError(f"Gemini API Error ({e.code}): {e.message}") from e

        except Exception as e:
            raise RuntimeError(f"Unexpected Error: {e}") from e