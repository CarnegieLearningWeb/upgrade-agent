import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    UPGRADE_API_URL = os.getenv('UPGRADE_API_URL', 'http://localhost:3030/api')
    UPGRADE_API_TIMEOUT = int(os.getenv("UPGRADE_API_TIMEOUT", 30))
    UPGRADE_SERVICE_ACCOUNT_KEY_PATH = os.getenv('UPGRADE_SERVICE_ACCOUNT_KEY_PATH', 'service-account-file.json')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    ANTHROPIC_API_TIMEOUT = int(os.getenv("UPGRADE_API_TIMEOUT", 30))
    ANTHROPIC_MODEL_NAME = os.getenv('ANTHROPIC_MODEL_NAME', 'claude-sonnet-4-20250514')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    def validate(self):
        """Validate required configuration."""
        if not self.UPGRADE_API_URL:
            raise ValueError("UPGRADE_API_URL is required")
        if not self.UPGRADE_API_TIMEOUT:
            raise ValueError("UPGRADE_API_TIMEOUT is required")
        if not os.path.exists(self.UPGRADE_SERVICE_ACCOUNT_KEY_PATH):
            raise ValueError(f"Service account file not found: {self.UPGRADE_SERVICE_ACCOUNT_KEY_PATH}")
        if not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")
        if not self.ANTHROPIC_API_TIMEOUT:
            raise ValueError("ANTHROPIC_API_TIMEOUT is required")
        if not self.ANTHROPIC_MODEL_NAME:
            raise ValueError("ANTHROPIC_MODEL_NAME is required")

config = Config()