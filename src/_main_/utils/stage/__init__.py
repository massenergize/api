from _main_.utils.stage.gtranslate_helper import MockGoogleTranslateClient
from _main_.utils.stage.secrets import get_s3_file
from _main_.utils.stage.logging import *
from dotenv import load_dotenv
from pathlib import Path  # python3 only
import os, socket
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
from _main_.utils.utils import load_json

class MassEnergizeApiEnvConfig:
    def __init__(self):
        self._set_api_run_info()
        self.secrets = None
        self.firebase_creds = None
        self.release_info = self.get_release_info()

    def load_env_variables(self):
        # this is the expected place we would usually put our .env file
        env_file_dir =  Path('.') / '.massenergize' / 'creds/'
        env_path = env_file_dir / f'{self.name}.env'
        self.load_env_vars_from_path(env_path)
        # in case there are actually some env files in the src/ folder itself, treat them as overriding anything prior
        self.load_override_env_vars()


    def get_allowlist_domains(self):
        domains =  os.getenv('DOMAIN_ALLOW_LIST', '').split(",")
        domains.append(self.get_ip_address())

        host_ip_addresses = os.getenv("HOST_IP_ADDRESSES", None)
        if host_ip_addresses:
            _addresses = host_ip_addresses.split(" ")
            domains.extend(_addresses)

        public_ip_v4  = os.getenv("PUBLIC_IPV4", None)
        if public_ip_v4:
            domains.append(public_ip_v4)

        public_ip_v6  = os.getenv("PUBLIC_IPV6", None)
        if public_ip_v6:
            domains.append(public_ip_v6)

        domains = [d.strip() for d in domains if d.strip()]
        return domains


    def get_firebase_auth(self):
        if self.firebase_creds:
            return self.firebase_creds

        firebase_s3_path: str =  os.getenv('FIREBASE_AUTH_KEY_PATH')
        firebase_local_path: str =  os.getenv('FIREBASE_AUTH_LOCAL_KEY_PATH')


        if os.environ.get('FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY') is not None:
            print(f"\033[90m Detected FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY in env file\033[0m")
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
            print(f"\033[90m Detected FIREBASE_AUTH_LOCAL_KEY_PATH so will fetch the firebase credentials from {firebase_local_path}\033[0m")
            firebase_creds = load_json(Path('.')/firebase_local_path)
        elif firebase_s3_path:
            print(f"\033[90m Detected FIREBASE_AUTH_KEY_PATH so will fetch the firebase credentials from s3://{firebase_s3_path}\033[0m")
            firebase_creds =  get_s3_file(firebase_s3_path)
        else:
            firebase_creds = {}

        self.firebase_creds = firebase_creds
        return firebase_creds

    def get_google_translate_key_file(self):
        path = os.getenv('GOOGLE_TRANSLATE_KEY_FILE_PATH')
        filename = os.getenv('GOOGLE_TRANSLATE_KEY_FILE_NAME')
        if not path or not filename:
            return None
        return f"{path}/{filename}"

    def set_up_google_translate_client(self):
        if self.is_test():
            return MockGoogleTranslateClient()

        google_translate_key_file = self.get_google_translate_key_file()

        if not google_translate_key_file:
            raise Exception("GOOGLE_TRANSLATE_KEY_FILE not found in environment variables")


        credentials = service_account.Credentials.from_service_account_file(
            filename=google_translate_key_file)

        # scopes = ['https://www.googleapis.com/auth/cloud-platform']
        return  translate.Client(credentials=credentials)

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

    def can_send_logs_to_cloudwatch(self):
        return not (self.is_local() or self.is_test())


    def get_logging_settings(self):
        if self.is_local() or self.is_test():
            return get_local_logging_settings()
        return get_default_logging_settings(self.name)


    def get_logger_identifier(self):
        return get_logger_name()



    def load_override_env_vars(self):
        env_path = Path('.') / '.env'
        self.load_env_vars_from_path(env_path)

        env_path = Path('.') / f'{self.name}.env'
        self.load_env_vars_from_path(env_path)

        if self.is_test():
            env_path = Path('.') / 'local.env'
            self.load_env_vars_from_path(env_path)

        if self.is_docker_mode and self.is_local():
            db_host =  os.getenv('DATABASE_HOST', "localhost")
            redis_host = os.getenv('CELERY_LOCAL_REDIS_BROKER_URL', "redis://localhost:6379/0")
            _local_hosts =  ['localhost', '127.0.0.1', '0.0.0.0']
            _docker_internal = "host.docker.internal"

            for _local_host in _local_hosts:
                if (_local_host in db_host):
                    db_host = db_host.replace(_local_host, _docker_internal)
                    os.environ.update({ 'DATABASE_HOST': db_host })
                if (_local_host in redis_host):
                    redis_host = redis_host.replace(_local_host, _docker_internal)
                    os.environ.update({ 'CELERY_LOCAL_REDIS_BROKER_URL': redis_host })


    def load_env_vars_from_path(self, env_path: Path):
        try:
            if not env_path.exists():
                return
            print(f"\033[90m Detected {env_path} env file, Loading credentials from it\033[0m")
            load_dotenv(env_path)
        except:
            print(f"\033[91m Something happened.  Could not load env variables from: {env_path}\033[0m")


    def _set_api_run_info(self):
        override_env = os.getenv("DJANGO_ENV")
        is_docker_mode = False
        
        current_run_file_path = Path('.') / '.massenergize'/ 'current_run_info.json'
        if not override_env and current_run_file_path.exists():
            _current_run_info = load_json(current_run_file_path)
            name = _current_run_info.get('django_env')
            assert name is not None, f"{current_run_file_path} should have django_env set to one of test, local, dev, canary or prod"
            is_docker_mode = _current_run_info.get('is_docker_mode')
            assert name is not None, f"{current_run_file_path} should have is_docker_mode set to true/false"
        else:
            load_dotenv()
            name = os.getenv("DJANGO_ENV", "dev")
            is_docker_mode = "DOCKER_CONTAINER" in os.environ

        name = name.lower()
        assert name in [ "test", "local", "dev", "canary", "prod"]
        self.name = name
        self.is_docker_mode = is_docker_mode
        print(f"\033[90m Detected | DJANGO_ENV => {self.name} | Docker Mode => {self.is_docker_mode}\033[0m")

    def get_ip_address(self):
        try:
            # Create a socket object to get the IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Connect to a well-known IP address (Google's public DNS server)
            ip_address = s.getsockname()[0]  # Get the IP address of the socket
            s.close()
            return ip_address
        except socket.error:
            return "Unable to get IP address"

    def get_release_info(self):
        release_info = load_json("release_info.json")
        return release_info

    def get_trusted_origins(self):
        origins = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(",")
        origins = [o.strip() for o in origins if o.strip()]
        return origins or []
