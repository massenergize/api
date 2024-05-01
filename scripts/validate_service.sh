#!/bin/bash

# Check if the Django API is running and responding
STATUS_CODE=$(curl --write-out %{http_code} --silent --output /dev/null http://localhost:8000/health_check)
echo $STATUS_CODE

if [ "$STATUS_CODE" -eq 200 ]; then
    echo "Deployment successful"
    exit 0 # Deployment successful
else
    cd /webapps/massenergize_api
    echo "Deployment failed"
    exit 1 # Deployment failed
fi