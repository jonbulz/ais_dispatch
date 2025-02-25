FROM python:3.10

WORKDIR /app

COPY dispatch.py .

RUN pip install psycopg2 requests

CMD ["python", "dispatch.py"]
