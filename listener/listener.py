import time
import json
from utils.db import insert_data, get_config_value
from pyais import TCPConnection

HOST = get_config_value("ais_host")
PORT = get_config_value("ais_port")


def ais_message_to_json(msg):
    # todo filtering
    data = {}
    if msg.msg_type < 4:
        data = {
            "timestamp": int(time.time()),
            "identifier": msg.mmsi,
            "lat": round(msg.lat, 3),
            "lon": round(msg.lon, 3),
            "cog": int(round(msg.course, 0)),
            "sog": int(round(msg.speed, 0)),
        }
    if msg.msg_type == 5:
        data = {
            "timestamp": int(time.time()),
            "identifier": msg.mmsi,
            "name": msg.shipname,
            "shiptype": msg.ship_type,
        }
    return json.dumps(data)


def listen_tcp():
    conn = TCPConnection(HOST, PORT)
    for msg in conn:
        decoded = msg.decode()
        mmsi = decoded.mmsi
        data = ais_message_to_json(decoded)
        insert_data(mmsi, data)


if __name__ == "__main__":
    listen_tcp()
