# Foodgram

[![Python](https://img.shields.io/badge/Python-3776AB?style=plastic&logo=python&logoColor=092E20&labelColor=white)](https://www.python.org/) [![Django](https://img.shields.io/badge/django-822e0d?style=plastic&logo=django&logoColor=092E20&labelColor=white)](https://www.djangoproject.com/) [![Django REST Framework](https://img.shields.io/badge/-Django_REST_framework-DC143C?style=red)](https://www.django-rest-framework.org/)

**Foodgram** — сайт для публикации рецептов, добавления их в избранное и подписки на других авторов. Для зарегистрированных пользователей доступен сервис "Список покупок" — формирование списка продуктов для выбранных рецептов.

## Технологии
- Django
- Django REST Framework
- Docker
- Nginx
- PostgreSQL

## Основные функции
- Проект разворачивается в Docker-контейнерах.
- Сценарий развертывания описан в `docker-compose.production.yml`.
- Настроен workflow для:
  - тестирования кода по PEP8
  - автоматического деплоя на сервер
  - отправки статуса в Telegram
- Поддержка загрузки "Списка покупок" в формате `.txt` с подсчитанным количеством ингредиентов.
- Генерация короткой ссылки для рецептов.
