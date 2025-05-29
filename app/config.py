# config.py

from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:Bentjun25%24@localhost:5432/momo_db"

    class Config:
        env_file = ".env"  # Optional if you want to load from a .env file later

# Create a settings object you can import everywhere
settings = Settings()
