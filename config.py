import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv('BOT_TOKEN') or ''
PINTEREST_EMAIL: str = os.getenv("PINTEREST_CSRFTOKEN") or ''
PINTEREST_PASSWORD: str = os.getenv("PINTEREST_SESSION") or ''
PINTEREST_CSRFTOKEN: str = os.getenv("PINTEREST_CSRFTOKEN") or ''
PINTEREST_SESSION: str = os.getenv("PINTEREST_SESSION") or ''