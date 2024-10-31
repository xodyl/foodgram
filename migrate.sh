#!/bin/bash

sudo docker compose exec backend python3 manage.py makemigrations users
sudo docker compose exec backend python3 manage.py makemigrations api
sudo docker compose exec backend python3 manage.py migrate 

