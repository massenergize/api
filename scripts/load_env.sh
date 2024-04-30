#!/bin/bash

cd /webapps/massenergize_api


# File to store environment variables
ENV_FILE=".env"

# Remove existing .env file if it exists
if [ -f "$ENV_FILE" ]; then
    rm "$ENV_FILE"
fi

sudo touch $ENV_FILE

# Run AWS Secrets Manager command to get secret value and store it in a variable
secret_json=$(aws secretsmanager get-secret-value --secret-id "api/dev" --query SecretString --output text --region "us-east-2")

# Check if the response is valid JSON
if [ $? -eq 0 ]; then
    # Parse JSON and extract key-value pairs
    IFS=$'\n'       # Set Internal Field Separator to newline
    env_lines=($(echo "$secret_json" | jq -r 'to_entries | .[] | "\(.key)=\"\(.value | gsub("\"";"\"\""))\""'))

    # Write to .env file
    for line in "${env_lines[@]}"; do
        echo "$line" >> .env
    done

    echo "Secrets successfully written to .env file."
else
    echo "Error: Failed to retrieve secrets from AWS Secrets Manager."
fi


echo "Environment variables from /etc/profile copied to $ENV_FILE"
