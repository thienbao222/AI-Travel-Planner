import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Multi-Agent AI Travel Planner"
    API_V1_STR: str = "/api"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Defaults
    DEFAULT_MODEL: str = "gemini-2.5-flash"  # Flexible, cost-efficient, and fast for agentic workflows

settings = Settings()
