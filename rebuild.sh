#!/bin/bash

sudo docker compose -f docker-compose.production.yml down --volume
# sudo docker compose down  
sudo docker compose -f docker-compose.production.yml up --build 

