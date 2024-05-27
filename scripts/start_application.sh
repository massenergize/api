#!/bin/bash

cd /webapps/massenergize/api

# Function to check and kill process on a given port
check_and_kill_process() {
    local port="$1"
    local pid=$(lsof -t -i:"$port")

    if [ -z "$pid" ]; then
        echo "No process is running on port $port."
    else
        # Kill the process
        kill -9 "$pid"
        echo "Killed process $pid running on port $port."
    fi
}

# Check and kill process on port 8000
check_and_kill_process 8000

# Check and kill process on port 80
check_and_kill_process 80

# Start the new Docker containers
sudo docker-compose up -d

# Wait for the containers to be ready
sleep 30