#!/bin/bash

cd /webapps/massenergize/api

sudo docker-compose down
sudo docker-compose down --remove-orphans
sudo docker stop $(docker ps -q) && sudo docker rm $(docker ps -aq)
sudo service docker restart
sudo docker image prune -f
sudo docker builder prune -f

# Build the new Docker images
sudo docker-compose build