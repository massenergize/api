import os, json, boto3, threading, tempfile, time
import sys
from pathlib import Path  # python3 only

import os
import json
import boto3
import threading

def fetch_secrets(django_env):
    """
    Fetch secrets from AWS Secrets Manager.
    """

    secret_name, secret_region = fetch_secret_id_and_region(django_env)

    # Initialize AWS Secrets Manager client
    client = boto3.client('secretsmanager', region_name=secret_region)

    # Retrieve secrets from AWS Secrets Manager
    response = client.get_secret_value(SecretId=secret_name)

    # Parse and return the secret as JSON
    secret = json.loads(response['SecretString'])
    return secret


def fetch_secret_id_and_region(django_env):
    """
    Fetch the secret ID and region from an S3 file.
    """

    passport_key_path = os.getenv("MASSENERGIZE_PASSPORT_KEY", None)
    if django_env not in ["dev", "canary", "prod"]:
        return None, None
    assert passport_key_path is not None, "You need to set MASSENERGIZE_PASSPORT_KEY in your env to proceed"
    double_slash_index = passport_key_path.find("//")
    if  double_slash_index > -1:
        passport_key_path = passport_key_path[double_slash_index+2:] # skip the double-slash //

    bucket, passport_key_file = passport_key_path.split("/")

    try:
        # Initialize AWS S3 client
        s3_client = boto3.client('s3')

        # Replace 'your_bucket_name' and 'your_file_key' with the actual bucket name and file key
        response = s3_client.get_object(Bucket=bucket, Key=passport_key_file)

        # Load the JSON content from the S3 file
        s3_data = json.loads(response['Body'].read().decode('utf-8'))

        # Extract secret ID and region from the JSON data
        secret_id = s3_data.get(django_env).get('secret_name')
        region = s3_data.get(django_env).get('region')

        return secret_id, region
    except:
        print("Could not connect to AWS.  You need fresh credentials.  Go to aws and get some fresh session keys here: https://d-9067fbc7f0.awsapps.com/")
        sys.exit(1)


def write_to_env_file(data, file_path):
    """
    Write the secrets data to a .env file.
    """
    with open(file_path, 'w') as file:
        for key, value in data.items():
            file.write(f"{key}=\"{value}\"\n")

def delete_file(file_path):
    """
    Delete the .env file after .5 minutes.
    """
    # Delete the .env file
    try:
        os.remove(file_path)
    except:
        "Finished deleting"

def get_secret_name_and_region():
    secret_name = os.getenv('SECRETS_ID', None)
    secret_region = os.getenv('SECRETS_TARGET_REGION', None)
    assert secret_name is not None, "Please ensure that you set SECRETS_ID in your environment"
    assert secret_region is not None, "Please ensure that you set SECRETS_TARGET_REGION in your environment"
    return secret_name, secret_region


def main():
    django_env = get_django_env()
    assert django_env is not None, "DJANGO_ENV is not set in the environment."

    django_env = django_env.lower()
    # Define the file path for the .env file
    env_file_dir =  Path('.') / '.massenergize/'

    os.makedirs(env_file_dir, exist_ok=True)

    if django_env not in ["local", "test"]:
        os.makedirs(env_file_dir / 'creds/', exist_ok=True)

        env_file_path =   env_file_dir / 'creds/' / f'{django_env}.env'
        delete_file(env_file_path)

        # Fetch secrets from AWS Secrets Manager
        secrets = fetch_secrets(django_env)

        # Write secrets data to the .env file
        write_to_env_file(secrets, env_file_path)

    djano_env_file_path = env_file_dir / 'current_django_env'
    with open(djano_env_file_path, 'w') as file:
        file.write(f"{django_env}\n")

def get_django_env():
    django_env = os.environ.get('DJANGO_ENV')

    if django_env is None:
        print("\033[93mDJANGO_ENV environment variable is not set.\033[0m")
        django_env = input("Please choose an environment mode (local, test, dev, canary, prod): ").strip().lower() or "local"
    else:
        django_env = django_env.strip().lower()

    if django_env not in ['local', 'test', 'dev', 'canary', 'prod']:
        print("\033[91mInvalid environment mode.\033[0m")
        return get_django_env()


    if django_env in ['dev', 'canary', 'prod']:
        confirm = input(f"\033[93mAre you sure you want to use '{django_env.upper()}' mode? (yes/no): \033[0m").strip().lower()
        if confirm not in ['yes', 'y']:
            print("\033[91mAborted. Please choose another environment mode.\033[0m")
            sys.exit(1)

        if django_env in ['canary', 'prod']:
            confirm = input(f"\033[92mFinal check: Are you sure you really sure you want to target '{django_env.upper()}'.  This is a production environment? (yes/no): \033[0m").strip().lower()
            if confirm not in ['yes', 'y']:
                print("\033[91mAborted. Please choose another environment mode.\033[0m")
                sys.exit(1)

    return django_env


if __name__ == "__main__":
    main()
