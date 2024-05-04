
import boto3, os, json
from botocore.exceptions import ClientError
from pathlib import Path
from dotenv import load_dotenv

# constants
TARGET_REGION = "us-east-2"


def get_secret(stage):
    assert stage is not None

    secret_name = f"api/{stage.lower()}"
    region_name = TARGET_REGION

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        print("Could not fetch credentials", e)
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
        path = file_path[file_path+1:]
        session = boto3.session.Session()
        s3 = session.client('s3')
        response = s3.get_object(bucket, path)
        file_content = response['Body'].read().decode('utf-8')

        # Parse the JSON content
        json_content = json.loads(file_content)
        print(json_content)

        return json_content
    except Exception as e:
        print("Could not load firebase file", e)
        return {}