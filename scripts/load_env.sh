#!/bin/bash

cd /webapps/massenergize/api


# File to store environment variables
ENV_FILE=".env"

# Remove existing .env file if it exists
if [ -f "$ENV_FILE" ]; then
    rm "$ENV_FILE"
fi

sudo touch $ENV_FILE

# Run AWS Secrets Manager command to get secret value and store it in a variable
source /etc/profile

secret_json=$(aws secretsmanager get-secret-value --secret-id "$SECRETS_ID" --query SecretString --output text --region "$SECRETS_TARGET_REGION")

# Check if the response is valid JSON
if [ $? -eq 0 ]; then
    # Parse JSON and extract key-value pairs
    env_lines=($(echo "$secret_json" | jq -r 'to_entries | .[] | select(.key != "FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY") | "\(.key)=\"\(.value | gsub("\"";"\"\""))\""'))
    # Write to .env file
    for line in "${env_lines[@]}"; do
        echo "$line" >> .env
    done

    echo "DJANGO_ENV=$BUILD_ENV" >> .env
    echo "DOCKER_MODE=true" >> .env
    echo "HOST_IP_ADDRESSES=\"$(hostname -I)\"" >> .env
    echo "Secrets successfully written to .env file."
else
    echo "Error: Failed to retrieve secrets from AWS Secrets Manager."
fi

get_and_write_public_ip() {
    token=$(curl -X PUT -H "X-aws-ec2-metadata-token-ttl-seconds: 300" -s http://169.254.169.254/latest/api/token)
    public_ip=$(curl -H "X-aws-ec2-metadata-token: $token" -s http://169.254.169.254/latest/meta-data/public-ipv4)
    
    echo "PUBLIC_IP=\"$public_ip\"" > .env
    echo "Public IP Address written to .env file: $public_ip"
}

get_and_write_public_ip
