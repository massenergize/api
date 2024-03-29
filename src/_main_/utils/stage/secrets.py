
import boto3, os, json
from botocore.exceptions import ClientError

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
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    if secret:
        return json.loads(secret)
    
    return {}
