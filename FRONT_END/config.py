# config.py

from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:Bentjun25%24@localhost:5432/momo_db"
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"  # if you want to load from a .env file later

# Create a settings object you can import
settings = Settings()
