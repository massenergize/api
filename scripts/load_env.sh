#!/bin/bash

cd /webapps/massenergize_api

# Create the .env file if it doesn't exist
sudo touch .env

# Loop through all environment variables
for var in $(env); do
  # Extract the variable name and value
  name="${var%=*}"
  value="${var#*=}"

  # Skip variables starting with '_' (usually internal variables)
  if [[ $name == '_' ]]; then
    continue
  fi

  # Skip variables starting with %
  if [[ $name == ^% ]]; then
    continue
  fi

  # Append the variable to the .env file in the format "NAME=VALUE"
  sudo echo "$name=$value" >> .env
done