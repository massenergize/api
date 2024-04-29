#!/bin/bash

cd /webapps/massenergize_api

sudo docker-compose down

# Build the new Docker images
sudo docker-compose build