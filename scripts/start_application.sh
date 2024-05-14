#!/bin/bash

cd /webapps/massenergize/api

# Start the new Docker containers
sudo docker-compose up -d

# Wait for the containers to be ready
sleep 30