from base64 import b64encode
from nacl import encoding, public
import requests
from dotenv import load_dotenv
from pathlib import Path  # python3 only
import os


PUBLIC_KEY_ROUTE = "https://api.github.com/repos/massenergize/api/actions/secrets/public-key"
LIST_SECRETS_ROUTE =  "https://api.github.com/repos/massenergize/api/actions/secrets"
PUT_SECRET_ROUTE = "https://api.github.com/repos/massenergize/api/actions/secrets"
KEYS = [
  "SECRET_KEY",
  "AWS_ACCESS_KEY_ID",
  "AWS_SECRET_ACCESS_KEY",
  "AWS_STORAGE_BUCKET_NAME",
  "AWS_S3_SIGNATURE_VERSION",
  "AWS_S3_REGION_NAME",
  "DATABASE_ENGINE",
  "DATABASE_NAME",
  "DATABASE_USER",
  "DATABASE_PASSWORD",
  "DATABASE_HOST",
  "DATABASE_PORT",
  "EMAIL",
  "EMAIL_PASSWORD",
  "EMAIL_PORT",
  "FIREBASE_API_KEY",
  "FIREBASE_AUTH_DOMAIN",
  "FIREBASE_PROJECT_ID",
  "FIREBASE_APP_ID",
  "FIREBASE_MESSAGE_SENDER_ID",
  "FIREBASE_DATABASE_URL",
  "FIREBASE_STORAGE_URL",
  "RECAPTCHA_SECRET_KEY",
  "RECAPTCHA_SITE_KEY",
  "FIREBASE_SERVICE_ACCOUNT_PROJECT_ID",
  "FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY_ID",
  "FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY",
  "FIREBASE_SERVICE_ACCOUNT_CLIENT_EMAIL",
  "FIREBASE_SERVICE_ACCOUNT_CLIENT_URL",
]


env_path = Path('.') / ('dev.env')
load_dotenv(dotenv_path=env_path, verbose=True)
AUTH = ('massenergize-admin', os.environ.get('GITHUB_TOKEN'))


def encrypt(public_key: str, secret_value: str) -> str:
  """Encrypt a Unicode string using the public key."""
  public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
  sealed_box = public.SealedBox(public_key)
  encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
  return b64encode(encrypted).decode("utf-8")


def update_dev_config(public_key):
  env_path = Path('.') / ('dev.env')
  load_dotenv(dotenv_path=env_path, verbose=True)
  for key in KEYS:
    res = requests.put(
      f"{PUT_SECRET_ROUTE}/DEV_{key}", 
      json={
        "key_id": public_key["key_id"], 
        "encrypted_value": encrypt(public_key["key"], os.environ.get(key))
      },
      auth=AUTH
    )
    print(key, res.text, res.status_code)


def update_prod_config(public_key):
  env_path = Path('.') / ('prod.env')
  load_dotenv(dotenv_path=env_path, verbose=True)
  for key in KEYS:
    res = requests.put(
      f"{PUT_SECRET_ROUTE}/{key}", 
      json={
        "key_id": public_key["key_id"], 
        "encrypted_value": encrypt(public_key["key"], os.environ.get(key))
      },
      auth=AUTH
    )
    print(key, res.text, res.status_code)



def transport():
  public_key = requests.get(PUBLIC_KEY_ROUTE, auth=AUTH)
  update_dev_config(public_key.json())
  update_prod_config(public_key.json())


if __name__ == "__main__":
    transport()