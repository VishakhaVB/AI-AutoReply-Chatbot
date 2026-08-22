import json
import logging
from typing import Dict, Literal
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai import errors
from src.config.settings import get_api_key

# --- Pydantic Schemas for Enforcing Gemini Structured Output ---

class LanguageAnalysis(BaseModel):
    language: Literal["English", "Hindi", "Marathi", "Hinglish"] = Field(
        description="The primary language of the message."
    )

class EmotionAnalysis(BaseModel):
    emotion: Literal["Happy", "Sad", "Angry", "Excited", "Neutral", "Stressed"] = Field(
        description="The emotional tone of the sender."
    )

class ReplyStyleAnalysis(BaseModel):
    reply_style: Literal["Formal", "Casual", "Funny", "Empathetic", "Motivational"] = Field(
        description="The recommended reply style based on context."
    )

class FullAnalysis(BaseModel):
    language: Literal["English", "Hindi", "Marathi", "Hinglish"] = Field(
        description="The language of the message."
    )
    emotion: Literal["Happy", "Sad", "Angry", "Excited", "Neutral", "Stressed"] = Field(
        description="The emotion of the message."
    )
    reply_style: Literal["Formal", "Casual", "Funny", "Empathetic", "Motivational"] = Field(
        description="The best reply style considering the emotion and sender relationship."
    )


# --- System Instruction Prompts ---

LANGUAGE_PROMPT = (
    "Identify the language of the provided chat message. "
    "Select exactly one from: English, Hindi, Marathi, Hinglish."
)

EMOTION_PROMPT = (
    "Analyze the emotional sentiment of the provided chat message. "
    "Select exactly one from: Happy, Sad, Angry, Excited, Neutral, Stressed."
)

REPLY_STYLE_PROMPT = (
    "Determine the best response tone/style given the input parameters: "
    "language, emotion, and relationship to the sender. "
    "Select exactly one from: Formal, Casual, Funny, Empathetic, Motivational."
)

FULL_ANALYSIS_PROMPT = (
    "Analyze the input message and user relationship. Determine: "
    "1. The language used (English, Hindi, Marathi, or Hinglish). "
    "2. The emotion (Happy, Sad, Angry, Excited, Neutral, or Stressed). "
    "3. The recommended reply style (Formal, Casual, Funny, Empathetic, or Motivational)."
)


class ConversationAnalyzer:
    """
    Analyzes chat messages using Gemini models to detect language, emotion,
    and suggest response styling. Output structures are validated using Pydantic.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        """
        Initializes the Gemini client with the local API key settings.
        
        Args:
            model_name (str): Model version to target. Defaults to 'gemini-2.5-flash'.
        """
        api_key = get_api_key()
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def detect_language(self, message: str) -> str:
        """
        Detects the language of the given message.
        
        Args:
            message (str): The chat message text.
            
        Returns:
            str: One of 'English', 'Hindi', 'Marathi', 'Hinglish'.
        """
        if not message or not message.strip():
            return "English"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"Message: {message}",
                config=types.GenerateContentConfig(
                    system_instruction=LANGUAGE_PROMPT,
                    response_mime_type="application/json",
                    response_schema=LanguageAnalysis,
                    temperature=0.0
                )
            )
            # Parse and validate the response structure
            result = LanguageAnalysis.model_validate_json(response.text)
            return result.language
        except (errors.APIError, Exception) as e:
            logging.error(f"Failed to detect language: {e}", exc_info=True)
            return "English"  # Safe fallback

    def detect_emotion(self, message: str) -> str:
        """
        Analyzes the emotional sentiment of the message.
        
        Args:
            message (str): The chat message text.
            
        Returns:
            str: One of 'Happy', 'Sad', 'Angry', 'Excited', 'Neutral', 'Stressed'.
        """
        if not message or not message.strip():
            return "Neutral"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"Message: {message}",
                config=types.GenerateContentConfig(
                    system_instruction=EMOTION_PROMPT,
                    response_mime_type="application/json",
                    response_schema=EmotionAnalysis,
                    temperature=0.0
                )
            )
            # Parse and validate the response structure
            result = EmotionAnalysis.model_validate_json(response.text)
            return result.emotion
        except (errors.APIError, Exception) as e:
            logging.error(f"Failed to detect emotion: {e}", exc_info=True)
            return "Neutral"  # Safe fallback

    def detect_reply_style(self, language: str, emotion: str, relationship: str) -> str:
        """
        Recommends a response style given message attributes and sender relation.
        
        Args:
            language (str): Message language.
            emotion (str): Message emotion.
            relationship (str): Relationship (e.g. friend, coworker).
            
        Returns:
            str: One of 'Formal', 'Casual', 'Funny', 'Empathetic', 'Motivational'.
        """
        context = f"Language: {language}\nEmotion: {emotion}\nRelationship: {relationship}"
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=context,
                config=types.GenerateContentConfig(
                    system_instruction=REPLY_STYLE_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ReplyStyleAnalysis,
                    temperature=0.0
                )
            )
            # Parse and validate the response structure
            result = ReplyStyleAnalysis.model_validate_json(response.text)
            return result.reply_style
        except (errors.APIError, Exception) as e:
            logging.error(f"Failed to detect reply style: {e}", exc_info=True)
            return "Casual"  # Safe fallback

    def analyze(self, message: str, relationship: str) -> Dict[str, str]:
        """
        Performs a full analysis run on a message, resolving language, emotion, and response style.
        
        Args:
            message (str): The chat message text.
            relationship (str): Relationship with the sender.
            
        Returns:
            Dict[str, str]: Dictionary containing keys 'language', 'emotion', 'reply_style'.
        """
        fallback_result = {
            "language": "English",
            "emotion": "Neutral",
            "reply_style": "Casual"
        }
        
        if not message or not message.strip():
            return fallback_result

        context = f"Message: {message}\nRelationship: {relationship}"
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=context,
                config=types.GenerateContentConfig(
                    system_instruction=FULL_ANALYSIS_PROMPT,
                    response_mime_type="application/json",
                    response_schema=FullAnalysis,
                    temperature=0.0
                )
            )
            # Validate complete response package
            result = FullAnalysis.model_validate_json(response.text)
            return {
                "language": result.language,
                "emotion": result.emotion,
                "reply_style": result.reply_style
            }
        except (errors.APIError, Exception) as e:
            logging.error(f"Failed to run complete conversation analysis: {e}", exc_info=True)
            return fallback_result
