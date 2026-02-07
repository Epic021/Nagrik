from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Nagrik API"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "nagrik"
    
    # JWT
    JWT_SECRET_KEY: str = "change-this-in-production-nagrik-secret-key-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24 * 7  # 1 week
    
    # Google Cloud
    GCS_BUCKET_NAME: str = "nagrik-uploads"
    GCS_SERVICE_ACCOUNT_KEY: str = ""  # Path to service account JSON
    GOOGLE_MAPS_API_KEY: str = ""
    
    # AI Services
    GEMINI_API_KEY: str = ""  # Google Gemini API key for classification
    
    # MS GraphRAG (for KG teammate)
    GRAPHRAG_ENDPOINT: str = ""  # e.g., http://localhost:8080
    GRAPHRAG_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
