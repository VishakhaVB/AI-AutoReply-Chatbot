import json
import logging
from typing import Dict, Any, Literal
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai import errors
from src.config.settings import get_api_key

# --- Pydantic Schemas for Structured JSON Formatting ---

class RiskResult(BaseModel):
    classification: Literal["Toxic", "Abusive", "Sensitive", "Personal Information", "Safe"] = Field(
        description="Category describing safety status of the message."
    )
    is_safe: bool = Field(
        description="True only if classification is 'Safe', False otherwise."
    )
    reason: str = Field(
        description="A brief description justifying the safety classification."
    )

class ThreeReplies(BaseModel):
    casual: str = Field(
        description="A casual, warm, conversational response."
    )
    funny: str = Field(
        description="A witty, funny, or roasting response."
    )
    professional: str = Field(
        description="A polite, clear, and professional response."
    )


# --- System Instruction Prompts ---

RISK_CHECK_PROMPT = (
    "Evaluate the safety of the input message. Classify it into exactly one of "
    "the following categories: Toxic, Abusive, Sensitive, Personal Information, Safe. "
    "Set is_safe to true only if the classification is 'Safe'."
)

REPLY_GENERATION_PROMPT = (
    "Analyze the provided chat history and user profile attributes. "
    "Generate three distinct reply candidates: 'casual', 'funny', and 'professional'. "
    "Tailor the tone and content according to the user profile."
)


class SafetyGuard:
    """
    Evaluates message safety and generates tone-specific reply alternatives
    using Gemini models with structured validation.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        """
        Initializes the SafetyGuard client using setting configurations.
        
        Args:
            model_name (str): Model variant to target. Defaults to 'gemini-2.5-flash'.
        """
        api_key = get_api_key()
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def check_risk(self, message: str) -> Dict[str, Any]:
        """
        Analyzes a message to detect toxicity, abuse, sensitive details, or PII.
        
        Args:
            message (str): Text content to inspect.
            
        Returns:
            Dict[str, Any]: Dictionary containing keys 'classification', 'is_safe', and 'reason'.
        """
        fallback_result = {
            "classification": "Toxic",
            "is_safe": False,
            "reason": "Failed to analyze message safety."
        }

        if not message or not message.strip():
            return {
                "classification": "Safe",
                "is_safe": True,
                "reason": "Message is empty."
            }

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"Message: {message}",
                config=types.GenerateContentConfig(
                    system_instruction=RISK_CHECK_PROMPT,
                    response_mime_type="application/json",
                    response_schema=RiskResult,
                    temperature=0.0
                )
            )
            result = RiskResult.model_validate_json(response.text)
            return {
                "classification": result.classification,
                "is_safe": result.is_safe,
                "reason": result.reason
            }
        except (errors.APIError, Exception) as e:
            logging.error(f"Failed to verify message safety: {e}", exc_info=True)
            return fallback_result

    def generate_three_replies(self, chat_history: str, user_profile: Dict[str, Any]) -> Dict[str, str]:
        """
        Generates casual, funny, and professional reply candidates based on logs and profile context.
        
        Args:
            chat_history (str): Contextual conversation log.
            user_profile (Dict[str, Any]): Dictionary containing user preferences/metadata.
            
        Returns:
            Dict[str, str]: Dictionary containing keys 'casual', 'funny', and 'professional'.
        """
        fallback_replies = {
            "casual": "Hey there!",
            "funny": "I'd reply, but I'm buffering.",
            "professional": "Thank you for your message."
        }

        if not chat_history or not chat_history.strip():
            return fallback_replies

        try:
            profile_str = json.dumps(user_profile, indent=2)
            context = f"User Profile:\n{profile_str}\n\nChat History:\n{chat_history}"
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=context,
                config=types.GenerateContentConfig(
                    system_instruction=REPLY_GENERATION_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ThreeReplies,
                    temperature=0.7
                )
            )
            result = ThreeReplies.model_validate_json(response.text)
            return {
                "casual": result.casual,
                "funny": result.funny,
                "professional": result.professional
            }
        except (errors.APIError, Exception) as e:
            logging.error(f"Failed to generate replies: {e}", exc_info=True)
            return fallback_replies

    def should_send(self, risk_result: Dict[str, Any]) -> bool:
        """
        Interprets safety evaluations to decide if a message is eligible to send.
        
        Args:
            risk_result (Dict[str, Any]): Evaluation data from check_risk.
            
        Returns:
            bool: True if safe to proceed, False otherwise.
        """
        if not risk_result:
            return False
        return bool(risk_result.get("is_safe", False)) and risk_result.get("classification") == "Safe"
