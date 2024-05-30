
import boto3,json
from pathlib import Path
from dotenv import load_dotenv

# constants
TARGET_REGION = "us-east-2"


def get_secret(stage):
    assert stage is not None
    secret_name = f"api/{stage.lower()}"

    # Create a Secrets Manager client
    try:
        get_secret_value_response = boto3.client('secretsmanager', region_name=TARGET_REGION).get_secret_value(
            SecretId=secret_name
        )
        print("Successfully got secrets")
    except Exception as e:
        print("Could not fetch credentials", e)
        import traceback
        traceback.print_exc()
        return load_env(stage)

    secret = get_secret_value_response['SecretString']
    if secret:
        res = json.loads(secret)
        return res
    
    return {}


def load_env(stage):
    try:
        env_path = Path('.') / f'{stage.lower()}.env'
        load_dotenv(dotenv_path=env_path)
    except Exception:
        load_dotenv()

    return {}

def get_s3_file(file_path):
    try:
        first_slash = file_path.index("/")
        bucket= file_path[:first_slash]
        path = file_path[first_slash+1:]
        response = boto3.client('s3').get_object(Bucket=bucket, Key=path)
        file_content = response['Body'].read().decode('utf-8')

        # Parse the JSON content
        json_content = json.loads(file_content)
        print("\033[90m Successfully loaded firebase credentials\033[0m")
        return json_content
    except Exception as e:
        print("\033[91m Could not load firebase file\033[0m", e)
        return {}