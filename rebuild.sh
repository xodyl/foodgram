#!/bin/bash

sudo docker compose -f docker-compose.production.yml down
sudo docker compose -f docker-compose.production.yml up --build 
