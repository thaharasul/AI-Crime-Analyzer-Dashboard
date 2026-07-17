import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models_store"
KB_DIR = BASE_DIR / "rag" / "knowledge_base"
CHROMA_DIR = BASE_DIR / "rag" / "chroma_store"

DATABASE_PATH = DATA_DIR / "crime_analyzer.db"
CRIME_CSV_PATH = DATA_DIR / "crime_data.csv"
TRAINED_MODEL_PATH = MODELS_DIR / "crime_predictor.pkl"
MODEL_METRICS_PATH = MODELS_DIR / "metrics.json"

for folder in (DATA_DIR, MODELS_DIR, CHROMA_DIR):
    folder.mkdir(parents=True, exist_ok=True)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    SESSION_TYPE = "filesystem"

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    GEMINI_API_KEY = GEMINI_API_KEY
    GEMINI_MODEL = GEMINI_MODEL
    EMBEDDING_MODEL = EMBEDDING_MODEL

    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"