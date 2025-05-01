# src/voice_concierge/config.py
from pydantic import BaseSettings, Field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # OpenAI API Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_org_id: Optional[str] = Field(None, env="OPENAI_ORG_ID")

    # Whisper Configuration
    whisper_model: str = Field("whisper-1", env="WHISPER_MODEL")

    # Vector Store Configuration
    vector_store_path: str = Field("./data/vector_store", env="VECTOR_STORE_PATH")

    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("./logs/voice_concierge.log", env="LOG_FILE")

    # Performance Configuration
    max_concurrency: int = Field(2, env="MAX_CONCURRENCY")
    chunk_size: int = Field(1000, env="CHUNK_SIZE")
    embedding_batch_size: int = Field(100, env="EMBEDDING_BATCH_SIZE")

    # Security Configuration
    encrypt_transcripts: bool = Field(False, env="ENCRYPT_TRANSCRIPTS")
    encrypt_key: Optional[str] = Field(None, env="ENCRYPT_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
