import psycopg2
import requests
import os

DATABASE_URL = os.getenv("DATABASE_URL")
REMOTE_HOST = "http://example.com/endpoint"


def dispatch():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT id, payload FROM data ORDER BY received_at ASC")
    rows = cursor.fetchall()

    for row in rows:
        data_id, payload = row
        response = requests.post(REMOTE_HOST, json={"data": payload})

        if response.status_code == 200:
            cursor.execute("DELETE FROM data WHERE id = %s", (data_id,))
            conn.commit()

    cursor.close()
    conn.close()


if __name__ == "__main__":
    dispatch()
