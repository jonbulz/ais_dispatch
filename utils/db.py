import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def insert_data(pk, payload):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE data SET payload = %s WHERE id = %s", (payload, pk))
    conn.commit()
    cursor.close()
    conn.close()
