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
    public_ipv4=$(curl -H "X-aws-ec2-metadata-token: $token" -s http://169.254.169.254/latest/meta-data/public-ipv4)
    public_ipv6=$(curl -H "X-aws-ec2-metadata-token: $token" -s http://169.254.169.254/latest/meta-data/public-ipv6)

    if [ -z "$public_ipv4" ] && [ -z "$public_ipv6" ]; then
        echo "Error: No public IP address assigned to the instance."
        exit 0
    fi

    if [ ! -z "$public_ipv4" ] && [ ${#public_ipv4} -le 16 ]; then
        echo "PUBLIC_IPV4=\"$public_ipv4\"" >> .env
        echo "PUBLIC_IPV4 Address written to .env file: $public_ipv4"
    fi

    if [ ! -z "$public_ipv6" ] && [ ${#public_ipv6} -le 40 ]; then
        echo "PUBLIC_IPV6=\"$public_ipv6\"" >> .env
        echo "PUBLIC_IPV6 Address written to .env file: $public_ipv6"
    fi

    if [ -z "$public_ipv4" ] && [ -z "$public_ipv6" ]; then
        echo "Error: No suitable public IP address(es) found."
    fi
}

get_and_write_public
