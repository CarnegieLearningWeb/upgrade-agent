import os
from typing import Optional, Dict
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from src.config.config import config
from src.models.constants import CONTENT_TYPE_JSON, ACCEPT_JSON
from src.exceptions.exceptions import AuthenticationError

class UpGradeAuth:
    def __init__(self):
        self.cached_token = None
        self.credentials = None
        self.service_account_key_path = config.UPGRADE_SERVICE_ACCOUNT_KEY_PATH

    def get_access_token(self) -> str:
        try:
            if not self.credentials:
                if not os.path.exists(self.service_account_key_path):
                    raise FileNotFoundError(f"Service account file not found: {self.service_account_key_path}")
                
                self.credentials = service_account.Credentials.from_service_account_file(
                    self.service_account_key_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )

            if not self.cached_token or self.credentials.expired:
                self.credentials.refresh(Request())
                self.cached_token = self.credentials.token

            return self.cached_token

        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    def get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        headers = {
            "Content-Type": CONTENT_TYPE_JSON,
            "Accept": ACCEPT_JSON
        }
        
        if include_auth:
            token = self.get_access_token()
            headers["Authorization"] = f"Bearer {token}"
        
        return headers


# Global auth instance
auth_manager = UpGradeAuth()