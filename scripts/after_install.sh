#!/bin/bash

cd /webapps/massenergize/api

sudo docker-compose down
sudo docker image prune -f
sudo docker builder prune -f

# Build the new Docker images
sudo docker-compose build