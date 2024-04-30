#!/bin/bash

cd /webapps/massenergize_api


# File to store environment variables
ENV_FILE=".env"

# Remove existing .env file if it exists
if [ -f "$ENV_FILE" ]; then
    rm "$ENV_FILE"
fi

sudo touch $ENV_FILE

# Check if /etc/profile exists
if [ -f "/etc/profile" ]; then
    # Read each line in /etc/profile
    while IFS= read -r line
    do
        # Check if the line starts with "export"
        if [[ "$line" == export\ * ]]; then
            # Extract the variable name and value
            var_name=$(echo "$line" | cut -d' ' -f2 | cut -d'=' -f1)
            var_value=$(echo "$line" | cut -d'=' -f2-)
            # Append the variable and value to .env file
            sudo echo "$var_name=$var_value" >> "$ENV_FILE"
        fi
    done < "/etc/profile"
fi

echo "Environment variables from /etc/profile copied to $ENV_FILE"
