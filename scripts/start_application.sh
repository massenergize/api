#!/bin/bash

cd /webapps/massenergize/api

# Function to check and kill process on a given port
# check_and_kill_process() {
#     local port="$1"
#     local pids=$(lsof -t -i:"$port")

#     if [ -z "$pids" ]; then
#         echo "No process is running on port $port."
#     else
#         # Set IFS to newline to handle newline-separated values
#         IFS=$'\n'
#         for pid in $pids; do
#             kill -9 "$pid"
#             echo "Killed process $pid running on port $port."
#         done
#         # Reset IFS to default value
#         unset IFS
#     fi
# }

# # Check and kill process on port 8000
# check_and_kill_process 8000

# # Check and kill process on port 80
# check_and_kill_process 80

# Start the new Docker containers
sudo docker-compose up -d

# Wait for the containers to be ready
sleep 30