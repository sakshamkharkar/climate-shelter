import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ClimateShelter AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Climate & Soil API Config
    CLIMATE_API_KEY: str = ""
    CLIMATE_API_BASE_URL: str = "https://api.open-meteo.com/v1"
    GEOCODING_API_BASE_URL: str = "https://geocoding-api.open-meteo.com/v1"
    SOIL_API_BASE_URL: str = "https://soil-weights.open-meteo.com/v1"
    
    # LLM Config
    LLM_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"  # gemini, openai, local
    
    # ANSYS Config
    ANSYS_MODE: str = "mock"  # mock, pymapdl, apdl_script
    ANSYS_EXECUTABLE_PATH: str = "C:/Program Files/ANSYS Inc/v231/ansys/bin/winx64/ansys231.exe"
    
    # Database
    DATABASE_URL: str = "sqlite:///./climateshelter.db"
    
    # App Settings
    DEMO_MODE: bool = True
    MODEL_DIR: str = os.path.join(os.path.dirname(__file__), "..", "models")
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "..", "data")
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

os.makedirs(settings.MODEL_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.DATA_DIR, "processed"), exist_ok=True)
os.makedirs(os.path.join(settings.DATA_DIR, "raw"), exist_ok=True)
