#!/bin/bash

echo "Stopping and removing Docker Compose containers..."
sudo docker compose down --volume
# sudo docker compose down  

echo "Restarting Docker Compose..."
sudo docker compose up --build 

echo "Done!"

