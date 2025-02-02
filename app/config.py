from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GGUF_MODEL_PATH: str = "storage/models/model.gguf"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    class Config:
        env_file = ".env"  # Automatically loads environment variables from .env

# Instantiate settings once to be used across the project
settings = Settings()
