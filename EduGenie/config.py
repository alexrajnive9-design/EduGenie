"""Central configuration for EduGenie. Values come from the .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
EXPLAIN_BACKEND: str = os.getenv("EXPLAIN_BACKEND", "local").strip().lower()
LOCAL_EXPLAIN_MODEL: str = "MBZUAI/LaMini-Flan-T5-783M"
