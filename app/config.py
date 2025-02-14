from pydantic_settings import BaseSettings
import os
import sqlite3

class Settings(BaseSettings):
    GGUF_MODEL_PATH: str = "storage/models/model.gguf"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DB_PATH: str = "summarization_queue.db"
    PROMPT_PASSWORD: str = "randompassword123"

    class Config:
        env_file = ".env"  # Automatically loads environment variables from .env

settings = Settings()

# Ensure the model path exists
if not os.path.exists(settings.GGUF_MODEL_PATH):
    raise FileNotFoundError(f"GGUF model not found at {settings.GGUF_MODEL_PATH}")

# Database connection setup
def get_db_connection():
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summarization_queue (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            result TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()