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


def fetch_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, payload FROM data ORDER BY received_at ASC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_config_value(key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM config WHERE key = %s;", (key,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None


def update_data_sent_size(size):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE config
        SET value = (value::BIGINT + %s)::TEXT
        WHERE key = 'data_sent';
    """, (size,))
    conn.commit()
    cursor.close()
    conn.close()
