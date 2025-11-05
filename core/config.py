from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "IRAS AI Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = ""
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"  # openai, anthropic, google
    
    # Vector Database
    VECTOR_DB_TYPE: str = "chroma"  # chroma, pinecone, weaviate
    CHROMA_DB_PATH: str = "./data/chroma_db"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    
    # Embeddings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:4200"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()