FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install gunicorn==20.1.0 && pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:9000", "backend.wsgi"]
