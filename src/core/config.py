
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    DATABASE_URL: str = "postgresql+psycopg2://user:password@localhost:5433/ai_bot_db" # <-- PORT CHANGED HERE

settings = Settings()