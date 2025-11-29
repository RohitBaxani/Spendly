import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings for Spendly backend."""

    google_api_key: str = os.getenv("GOOGLE_API_KEY", "AIzaSyAeLtjcHBUVIyXIlUhte8qIKb-JwpoA0f4")
    model_name: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

    backend_base_dir: str = os.path.dirname(os.path.abspath(__file__))
    uploads_dir: str = os.path.join(backend_base_dir, "..", "uploads")
    sessions_dir: str = os.path.join(backend_base_dir, "..", "data", "sessions")


settings = Settings()


