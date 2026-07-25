import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AI Research & Knowledge Assistant"
    API_V1_STR: str = "/api/v1"
    
    # Storage Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    RAW_DOCUMENTS_DIR: str = os.path.join(DATA_DIR, "raw_documents")
    VECTOR_DB_DIR: str = os.path.join(DATA_DIR, "vector_db")
    DATASET_DIR: str = os.path.join(DATA_DIR, "dataset")
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")
    DATABASE_PATH: str = os.path.join(DATA_DIR, "assistant.db")
    
    # Model Artifact Paths
    CLASSIFIER_MODEL_PATH: str = os.path.join(MODELS_DIR, "tf_classifier.h5")
    TOKENIZER_PATH: str = os.path.join(MODELS_DIR, "tokenizer.pickle")
    
    # LLM & Embedding configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"
    
    # Chunking parameters
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure mandatory directories exist
os.makedirs(settings.RAW_DOCUMENTS_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
os.makedirs(settings.DATASET_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
