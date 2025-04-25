import time
import json
import os
import signal
import sys
from utils.db import insert_data, update_status
from pyais import TCPConnection

SERVICE = "listener"
HOST = os.getenv("AIS_HOST")
PORT = int(os.getenv("AIS_PORT"))
SYSTEM_EXIT = False


def handle_shutdown(signum, frame):
    global SYSTEM_EXIT
    print(f"Signal {signum} received. Shutting down...")
    SYSTEM_EXIT = True
    update_status(SERVICE, "inactive")
    sys.exit(0)


def ais_message_to_json(msg):
    # todo filtering
    if msg.msg_type < 4:
        data = {
            "timestamp": int(time.time()),
            "identifier": msg.mmsi,
            "lat": round(msg.lat, 3),
            "lon": round(msg.lon, 3),
            "cog": int(round(msg.course, 0)),
            "sog": int(round(msg.speed, 0)),
        }
    elif msg.msg_type == 5:
        data = {
            "timestamp": int(time.time()),
            "identifier": msg.mmsi,
            "name": msg.shipname,
            "shiptype": msg.ship_type,
        }
    else:
        data = {}
    return json.dumps(data)


def listen_tcp():
    conn = TCPConnection(HOST, PORT)
    for msg in conn:
        decoded = msg.decode()
        mmsi = decoded.mmsi
        data = ais_message_to_json(decoded)
        insert_data(mmsi, data)

# todo listen_udp


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


def run_listener():
    update_status(SERVICE, "active")
    try:
        while not SYSTEM_EXIT:
            listen_tcp()
    except Exception as e:
        err_msg = str(e) or repr(e)
        update_status(SERVICE, "error", err_msg)
        print(f"Error: {err_msg}")


if __name__ == "__main__":
    run_listener()
