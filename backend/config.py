"""ProBharatAI Configuration Module"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'probharatai.db'}")

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "probharatai-secret-change-me")

# LLM Configuration
DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Browser Automation
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
DEFAULT_BROWSER = os.getenv("DEFAULT_BROWSER", "chromium")

# Security
REQUIRE_APPROVAL = os.getenv("REQUIRE_APPROVAL", "true").lower() == "true"
MAX_ACTIONS_WITHOUT_APPROVAL = int(os.getenv("MAX_ACTIONS_WITHOUT_APPROVAL", 5))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = DATA_DIR / "probharatai.log"
