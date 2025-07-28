from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str
    
    # Qdrant
    QDRANT_HOST: str
    QDRANT_PORT: int
    QDRANT_COLLECTION_NAME: str
    
    # Redis
    REDIS_URL: str
    
    # LLM
    GOOGLE_API_KEY: str
    
    # Email
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_SENDER_EMAIL: str
    SMTP_SENDER_PASSWORD: str

    class Config:
        env_file = ".env"

settings = Settings()