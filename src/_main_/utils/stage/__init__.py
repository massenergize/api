import secrets
from _main_.utils.stage.secrets import get_s3_file, get_secret, load_env
from _main_.utils.stage.logging import *
from dotenv import load_dotenv
from pathlib import Path  # python3 only
import os, boto3

from _main_.utils.utils import load_json

class MassEnergizeApiEnvConfig:
    def __init__(self):
        name = self.get_current_env()
        print(f"Detected | DJANGO_ENV={name}")
        assert name in [ "test", "local", "dev", "canary", "prod"]

        self.name = name
        self.secrets = None
        self.firebase_creds = None
    
    def load_env_variables(self):
        # this is the expected place we would usually put our .env file
        env_file_dir =  Path('.') / '.massenergize/' / 'creds/'
        env_path = env_file_dir / f'{self.name}.env'
        self.load_env_vars_from_path(env_path)
        # in case there are actually some env files in the src/ folder itself, treat them as overriding anything prior
        self.load_override_env_vars()


    def get_allowlist_domains(self):
        return os.getenv('DOMAIN_ALLOW_LIST', '').split(",")


    def get_firebase_auth(self):
        if self.firebase_creds:
            return self.firebase_creds
        
        firebase_s3_path: str =  os.getenv('FIREBASE_AUTH_KEY_PATH')
        firebase_local_path: str =  os.getenv('FIREBASE_AUTH_LOCAL_KEY_PATH')


        if os.environ.get('FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY') is not None:
            print(f"Detected FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY in .env file")
            firebase_creds =  {
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

        elif firebase_local_path:
            print(f"Detected FIREBASE_AUTH_LOCAL_KEY_PATH so will fetch the firebase credentials from {firebase_local_path}")
            firebase_creds = load_json(Path('.')/firebase_local_path)
        elif firebase_s3_path:
            print(f"Detected FIREBASE_AUTH_KEY_PATH so will fetch the firebase credentials from s3://{firebase_s3_path}")
            firebase_creds =  get_s3_file(firebase_s3_path)
        else:
            firebase_creds = {}

        self.firebase_creds = firebase_creds
        return firebase_creds


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
        if self.is_local() or not self.secrets:
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

    def load_override_env_vars(self):
        env_path = Path('.') / '.env'
        self.load_env_vars_from_path(env_path)  

        env_path = Path('.') / f'{self.name}.env'
        self.load_env_vars_from_path(env_path)


    def load_env_vars_from_path(self, env_path: Path):
        try:
            if not env_path.exists():
                return
            print(f"Detected {env_path} env file, Loading credentials from it")
            load_dotenv(env_path)
        except:
            print(f"Something happened.  Could not load env variables from: {env_path}")


    def get_current_env(self):

        django_env = os.environ.get("DJANGO_ENV", None)
        if django_env:
            return django_env

        current_env_path = Path('.') / '.massenergize'/ 'current_django_env'
        if current_env_path.exists():
            with open(current_env_path, 'r') as file:
                django_env = file.read().strip().lower()
        else:
            # default
            django_env = "local"
        
        return django_env