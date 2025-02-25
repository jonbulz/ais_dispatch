FROM python:3.10

WORKDIR /app

COPY listener.py .

RUN pip install psycopg2 requests pyais

CMD ["python", "listener.py"]
