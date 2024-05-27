#!/bin/bash

cd /webapps/massenergize/api

# Find the process ID (PID) using lsof to check for any process listening on port 8000
PID=$(lsof -t -i:8000)

# Check if a PID was found
if [ -z "$PID" ]; then
    echo "No process is running on port 8000."
else
    # Kill the process
    kill -9 $PID
    echo "Killed process $PID running on port 8000."
fi


# Start the new Docker containers
sudo docker-compose up -d

# Wait for the containers to be ready
sleep 30