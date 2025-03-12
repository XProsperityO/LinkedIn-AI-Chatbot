import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Bot configuration
MAX_CONNECTIONS_PER_DAY = int(os.getenv("MAX_CONNECTIONS_PER_DAY", "25"))
MAX_MESSAGES_PER_DAY = int(os.getenv("MAX_MESSAGES_PER_DAY", "15"))
HEADLESS_BROWSER = os.getenv("HEADLESS_BROWSER", "True").lower() == "true"

# Target audience configuration
TARGET_INDUSTRIES = os.getenv("TARGET_INDUSTRIES", "Technology,Marketing,Sales").split(",")
TARGET_TITLES = os.getenv("TARGET_TITLES", "CEO,CTO,Director,Manager").split(",")
TARGET_LOCATIONS = os.getenv("TARGET_LOCATIONS", "").split(",")

# Database
DB_PATH = os.getenv("DB_PATH", "linkedin_bot.sqlite3")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "linkedin_bot.log")