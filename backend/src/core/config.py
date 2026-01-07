from dotenv import load_dotenv
import os

load_dotenv()

LLM_CONFIG = {
    "model": "gemini-1.5-flash",
    "temperature": 0.5,
    "google_api_key": os.getenv("GOOGLE_API_KEY")
}

SUPABASE_CONFIG = {
    "url": os.getenv("SUPABASE_URL"),
    "key": os.getenv("SUPABASE_KEY"),
}