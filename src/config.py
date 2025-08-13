import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    UPGRADE_API_URL = os.getenv('UPGRADE_API_URL', 'http://localhost:3030/api')
    UPGRADE_SERVICE_ACCOUNT_KEY_PATH = os.getenv('UPGRADE_SERVICE_ACCOUNT_KEY_PATH', 'service-account-file.json')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    MODEL_NAME = os.getenv('MODEL_NAME', 'claude-sonnet-4-20250514')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

config = Config()