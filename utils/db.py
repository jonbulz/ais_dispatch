import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def insert_data(pk, payload):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO data (id, payload)
        VALUES (%s, %s)
        ON CONFLICT (id)
        DO UPDATE SET payload = EXCLUDED.payload
    """, (pk, payload))
    conn.commit()
    cursor.close()
    conn.close()


def fetch_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, payload FROM data WHERE sent_at is null ORDER BY received_at ASC")
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


def update_config_value(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE config SET value = %s WHERE key = %s;
    """, (value, key))
    conn.commit()
    cursor.close()
    conn.close()


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


def update_sent_at_timestamp(id, timestamp):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE data
        SET sent_at= %s
        WHERE id = %s;
    """, (timestamp, id,))
    conn.commit()
    cursor.close()
    conn.close()


def get_status(service):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status, info FROM status WHERE service = %s
    """, (service,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"status": result[0], "info": result[1]} if result else None


def update_status(service, status, info=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO status (service, status, info)
        VALUES (%s, %s, %s)
        ON CONFLICT (service)
        DO UPDATE SET 
            status = EXCLUDED.status,
            info = EXCLUDED.info;
    """, (service, status, info))
    conn.commit()
    cursor.close()
    conn.close()
