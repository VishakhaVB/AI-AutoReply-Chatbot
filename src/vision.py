import logging
from pathlib import Path
from typing import Dict, Literal
from pydantic import BaseModel, Field
from PIL import Image, UnidentifiedImageError
from google import genai
from google.genai import types
from google.genai import errors
from src.config.settings import get_api_key

# --- Pydantic Schema for Structured Vision Output ---

class ImageAnalysis(BaseModel):
    image_type: Literal[
        "Handwritten Notes",
        "Printed Document",
        "Timetable",
        "Screenshot",
        "Meme",
        "Other"
    ] = Field(
        description="The classification category that best describes the type of image input."
    )
    description: str = Field(
        description="A clear and comprehensive textual description detailing what is shown in the image."
    )
    extracted_text: str = Field(
        description="A transcript of any text characters, notes, or letters recognized in the image. Return empty string if none."
    )

# --- System Instruction Prompt ---

IMAGE_ANALYSIS_PROMPT = (
    "Analyze the provided image and extract its properties. Determine: "
    "1. The category of the image (Handwritten Notes, Printed Document, Timetable, Screenshot, Meme, or Other). "
    "2. A detailed description of the content. "
    "3. A transcription of any visible text found within the image."
)


class VisionAnalyzer:
    """
    Interfaces with Google's Gemini Vision models to analyze local images,
    providing classification, descriptions, and text extraction (OCR).
    """

    def __init__(self, model_name: str = "gemini-3.6-flash") -> None:
        """
        Initializes the VisionAnalyzer.
        
        Args:
            model_name (str): Model name to execute vision analysis. Defaults to 'gemini-3.6-flash'.
        """
        api_key = get_api_key()
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def analyze_image(self, image_path: str) -> Dict[str, str]:
        """
        Performs a full multimodal analysis on a local image file.
        
        Args:
            image_path (str): Absolute or relative filesystem path to the image.
            
        Returns:
            Dict[str, str]: Dictionary containing:
                - 'image_type': Class classification string.
                - 'description': Content description.
                - 'extracted_text': Raw text transcription.
                
        Raises:
            FileNotFoundError: If the file path does not point to a valid file.
            ValueError: If the file format is corrupt or unsupported by Pillow.
            RuntimeError: If the Gemini API call or parsing fails.
        """
        path = Path(image_path)
        
        # Verify file existence
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Image file not found at path: '{image_path}'")

        try:
            # Load and verify format compatibility using Pillow
            with Image.open(path) as img:
                img.verify()
            
            # Reopen the image to pass standard data stream to Gemini
            with Image.open(path) as img:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[IMAGE_ANALYSIS_PROMPT, img],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ImageAnalysis,
                        temperature=0.0
                    )
                )
                
                result = ImageAnalysis.model_validate_json(response.text)
                return {
                    "image_type": result.image_type,
                    "description": result.description,
                    "extracted_text": result.extracted_text
                }
                
        except UnidentifiedImageError as e:
            logging.error(f"File is not a supported or valid image format: {image_path}")
            raise ValueError(f"File is not a supported or valid image format: {image_path}") from e
        except errors.APIError as e:
            logging.error(f"Gemini API error during image analysis: {e.message}")
            raise RuntimeError(f"Gemini API vision request failed: {e.message}") from e
        except Exception as e:
            logging.error(f"Unexpected error analyzing image {image_path}: {e}", exc_info=True)
            raise RuntimeError(f"Unexpected vision analysis failure: {e}") from e

    def describe_image(self, image_path: str) -> str:
        """
        Generates a textual description of the image content.
        
        Args:
            image_path (str): Filepath of the image.
            
        Returns:
            str: Described content, or empty string on failure.
        """
        try:
            analysis = self.analyze_image(image_path)
            return analysis.get("description", "")
        except Exception as e:
            logging.error(f"Failed to generate description for {image_path}: {e}")
            return ""

    def extract_text(self, image_path: str) -> str:
        """
        Transcribes any readable text located in the image.
        
        Args:
            image_path (str): Filepath of the image.
            
        Returns:
            str: Extracted text contents, or empty string on failure.
        """
        try:
            analysis = self.analyze_image(image_path)
            return analysis.get("extracted_text", "")
        except Exception as e:
            logging.error(f"Failed to extract text from {image_path}: {e}")
            return ""

    def detect_image_type(self, image_path: str) -> str:
        """
        Detects and classifies the image type.
        
        Args:
            image_path (str): Filepath of the image.
            
        Returns:
            str: Class category name or 'Other' on failure.
        """
        try:
            analysis = self.analyze_image(image_path)
            return analysis.get("image_type", "Other")
        except Exception as e:
            logging.error(f"Failed to classify image type for {image_path}: {e}")
            return "Other"
