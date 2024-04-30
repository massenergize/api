#!/bin/bash

cd /webapps/massenergize_api


# File to store environment variables
ENV_FILE=".env"

# Remove existing .env file if it exists
if [ -f "$ENV_FILE" ]; then
    rm "$ENV_FILE"
fi

sudo touch $ENV_FILE

# # Check if /etc/profile exists
# if [ -f "/etc/profile" ]; then
#     # Read each line in /etc/profile
#     while IFS= read -r line
#     do
#         # Check if the line starts with "export"
#         if [[ "$line" == export\ AWS_ACCESS_KEY_ID=* || "$line" == export\ AWS_SECRET_ACCESS_KEY=* || "$line" == export\ AWS_S3_SIGNATURE_VERSION=* || "$line" == export\ AWS_S3_REGION_NAME=* || "$line" == export\ AWS_DEFAULT_REGION=* ]]; then
#             # Extract the variable name and value
#             var_name=$(echo "$line" | cut -d' ' -f2 | cut -d'=' -f1)
#             var_value=$(echo "$line" | cut -d'=' -f2-)
            
#             # Check if the variable value spans multiple lines
#             while [[ "$var_value" != *\"* ]]; do
#                 read -r next_line
#                 var_value="$var_value $next_line"
#             done
            
#             # Append the variable and value to .env file
#             echo "$var_name=$var_value" >> "$ENV_FILE"
#         fi
#     done < "/etc/profile"
# fi

# Run AWS Secrets Manager command to get secret value and store it in a variable
secret_json=$(aws secretsmanager get-secret-value --secret-id "$SECRETS_ID" --query SecretString --output text --region "us-east-2")

# Check if the response is valid JSON
if [ $? -eq 0 ]; then
    # Parse JSON and extract key-value pairs
    IFS=$'\n'       # Set Internal Field Separator to newline
    env_lines=($(echo "$secret_json" | jq -r 'to_entries | .[] | "\(.key)=\(.value)"'))

    # Write to .env file
    for line in "${env_lines[@]}"; do
        echo "$line" >> .env
    done

    echo "Secrets successfully written to .env file."
else
    echo "Error: Failed to retrieve secrets from AWS Secrets Manager."
fi


echo "Environment variables from /etc/profile copied to $ENV_FILE"
