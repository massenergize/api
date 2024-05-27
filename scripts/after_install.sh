#!/bin/bash

cd /webapps/massenergize/api

sudo docker-compose down
sudo docker-compose down --remove-orphans
sudo docker image prune -f
sudo docker builder prune -f
sudo service docker start

# Build the new Docker images
sudo docker-compose build