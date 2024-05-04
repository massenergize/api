from _main_.utils.stage.secrets import get_s3_file, get_secret
from _main_.utils.stage.logging import *
from dotenv import load_dotenv
from pathlib import Path  # python3 only
import os

class Stage:
    def __init__(self, name):
        self.name = name.lower()
        self.secrets = None
    
    def get_secrets(self):
        if self.secrets:
            return self.secrets
        
        if self.is_local():
            self.secrets =  self.load_local_env()
        else:
            self.secrets = get_secret(self.name)
        
        return self.secrets

    def get_allowlist_domains(self):
        domains =  self.get_secrets().get('DOMAIN_ALLOW_LIST', '')
        if not domains:
            return []
        
        return domains.split(",")


    def get_firebase_auth(self):
        if self.is_local():
            return {
              "type": "service_account",
              "project_id": os.environ.get('FIREBASE_SERVICE_ACCOUNT_PROJECT_ID'),
              "private_key_id": os.environ.get('FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY_ID'),
              "private_key": os.environ.get('FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY'),
              "client_email": os.environ.get('FIREBASE_SERVICE_ACCOUNT_CLIENT_EMAIL'),
              "client_id": os.environ.get('FIREBASE_SERVICE_ACCOUNT_CLIENT_ID'),
              "client_x509_cert_url": os.environ.get('FIREBASE_SERVICE_ACCOUNT_CLIENT_URL'),
              "auth_uri": "https://accounts.google.com/o/oauth2/auth",
              "token_uri": "https://oauth2.googleapis.com/token",
              "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            }
        secrets = self.get_secrets()
        firebase_path: str =  secrets and secrets.get('FIREBASE_AUTH_KEY_PATH')
        return get_s3_file(firebase_path)


    def is_prod(self):
        return self.name == "prod"

    def is_canary(self):
        return self.name == "canary"

    def is_dev(self):
        return self.name == "dev"

    def is_local(self):
        return self.name == "local"

    def is_test(self):
        return self.name == "test"


    def get_logging_settings(self):
        if self.is_local():
            return get_local_logging_settings()
        return get_default_logging_settings(self.name)


    def get_logger_identifier(self):
        return get_logger_name()


    def load_local_env(self):
        try:
            env_path = Path('.') / 'local.env'
            load_dotenv(dotenv_path=env_path)
        except Exception:
            load_dotenv()

        return {}