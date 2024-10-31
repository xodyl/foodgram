#!/bin/bash

CONTAINER_NAME="foodgram-db-1" 
DB_USER="foodgram_user"
DB_NAME="foodgram"

INGREDIENTS_CSV="./data/ingredients.csv"
INGREDIENTS_TABLE="api_ingredient"

TAGS_CSV="./data/tags.csv"
TAGS_TABLE="api_tag"

sudo docker cp "$INGREDIENTS_CSV" "$CONTAINER_NAME:/ingredients.csv"

sudo docker exec -it "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "ALTER SEQUENCE ${INGREDIENTS_TABLE}_id_seq MINVALUE 0 RESTART WITH 0;"

sudo docker exec -it "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "\COPY $INGREDIENTS_TABLE(name, measurement_unit) FROM '/ingredients.csv' DELIMITER ',' CSV HEADER;"

sudo docker exec -it "$CONTAINER_NAME" rm /ingredients.csv


sudo docker cp "$TAGS_CSV" "$CONTAINER_NAME:/tags.csv"

sudo docker exec -it "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "ALTER SEQUENCE ${TAGS_TABLE}_id_seq MINVALUE 0 RESTART WITH 0;"

sudo docker exec -it "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "\COPY $TAGS_TABLE(name, slug) FROM '/tags.csv' DELIMITER ',' CSV HEADER;"

sudo docker exec -it "$CONTAINER_NAME" rm /tags.csv

