import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory (root directory of the project where .env is located)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

def get_api_key() -> str:
    """
    Retrieves the Gemini API key from environment variables.
    
    Returns:
        str: The retrieved Gemini API key.
        
    Raises:
        ValueError: If the GEMINI_API_KEY environment variable is not defined or is empty.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "CRITICAL CONFIGURATION ERROR: The 'GEMINI_API_KEY' environment variable "
            "is missing or empty. Please set it in your '.env' file or export it "
            "as an environment variable."
        )
    return api_key
