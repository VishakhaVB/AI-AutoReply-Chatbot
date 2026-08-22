import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory (root directory of the project where .env is located)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Path to the .env file
ENV_PATH = BASE_DIR / ".env"

# Load environment variables from the .env file if it exists
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

class Settings:
    """
    Application configuration settings.
    
    Reads configuration values from environment variables. Critical settings
    such as API keys are retrieved dynamically and never hardcoded.
    """
    
    # Debug / Development flag
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    
    # OpenAI API Configuration
    # Note: These values are retrieved from environment variables and not hardcoded.
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Automation Configurations
    POLLING_INTERVAL_SECONDS: float = float(os.getenv("POLLING_INTERVAL_SECONDS", "5.0"))
    
    # Chat Parsing Configuration
    TARGET_SENDER_NAME: str = os.getenv("TARGET_SENDER_NAME", "Rohan Das")
    SYSTEM_PROMPT: str = os.getenv(
        "SYSTEM_PROMPT",
        "You are a person named Naruto who speaks Hindi as well as English. "
        "You are from India and you are a coder. You analyze chat history "
        "and roast people in a funny way. Output should be the next chat "
        "response (text message only)."
    )

    def validate(self) -> None:
        """
        Validate critical environment configuration settings.
        
        Raises:
            ValueError: If a required configuration (like OPENAI_API_KEY) is missing.
        """
        if not self.OPENAI_API_KEY:
            raise ValueError(
                "CRITICAL CONFIGURATION ERROR: 'OPENAI_API_KEY' is not set.\n"
                "Please define it in your .env file or export it as an environment variable."
            )

# Instantiate a single configuration settings object
settings = Settings()
