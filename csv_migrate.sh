#!/bin/bash

sudo docker cp ./data/tags.csv foodgram-backend-1:/app/data/tags.csv
sudo docker cp ./data/ingredients.csv foodgram-backend-1:/app/data/ingredients.csv
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_data --ingredients data/ingredients.csv --tags data/tags.csv

