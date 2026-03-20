import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não definida no .env")
