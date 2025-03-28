import requests
import io
import os
import csv
import time
import json
from urllib.parse import urljoin
from utils.db import get_config_value, fetch_data, update_data_sent_size, update_sent_at_timestamp
from datetime import datetime


class Dispatcher:
    def __init__(self):
        self.remote_host = os.getenv("REMOTE_SERVER_ADDRESS")
        self.user = os.getenv("REMOTE_SERVER_USER")
        self.secret = os.getenv("REMOTE_SERVER_PW")
        self.token = None

    @staticmethod
    def can_send_data(payload):
        data_max = int(get_config_value("data_max") or 0)
        data_sent = int(get_config_value("data_sent") or 0)
        return len(payload) <= data_max - data_sent

    @staticmethod
    def is_active():
        return get_config_value("active")

    @staticmethod
    def _ais_to_csv(data):
        out = io.StringIO()

        # todo define cols in a central place?
        cols = ["timestamp", "identifier", "lat", "lon", "cog", "sog"]
        required = ["timestamp", "identifier", "lat", "lon"]
        writer = csv.DictWriter(out, fieldnames=cols)
        writer.writeheader()
        for identifier, vals in data:
            # DictWriter is strict about matching the columns
            # so we need to filter our values
            vals = json.loads(vals)
            vals = {k: v for k, v in vals.items() if k in cols}
            incomplete_data = {key for key in required if not vals.get(key)}
            if incomplete_data:
                continue
            row = {"identifier": identifier, **vals}
            writer.writerow(row)
        csv_data = out.getvalue()
        out.close()
        return csv_data

    def _get_new_token(self):
        url = urljoin(self.remote_host, "token/")
        headers = {"Content-Type": "application/json"}
        credentials = {"username": self.user, "password": self.secret}
        data = json.dumps(credentials)
        auth_response = self._send_request("POST", url, headers=headers, data=data)
        auth_response.raise_for_status()
        token = auth_response.json().get("access")
        return token

    def _update_token(self, token=None):
        if not token:
            token = self._get_new_token()
        self.token = token

    @staticmethod
    def _send_request(method, url, **kwargs):
        """
        Wrapper to track sent data size
        :param method: HTTP method
        :param url: The request url
        :return: Response object
        """
        headers_size = sum(len(k) + len(v) for k, v in kwargs.get("headers", {}).items())
        body_size = len(kwargs.get("data", b"")) if "data" in kwargs else 0
        json_size = len(str(kwargs.get("json", ""))) if "json" in kwargs else 0

        total_sent_size = headers_size + body_size + json_size

        response = requests.request(method, url, **kwargs)

        update_data_sent_size(total_sent_size)

        return response

    def _authenticate_request(self, method, url, **kwargs):
        """
        Wrapper to handle authentication
        :param method: HTTP method
        :param url: The request url
        :return: Response object
        """
        if not self.token:
            self._update_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"

        response = self._send_request(method, url, headers=headers, **kwargs)
        if response.status_code == 401:
            self._update_token()
            headers["Authorization"] = f"Bearer {self.token}"
            response = self._send_request(method, url, headers=headers, **kwargs)

        response.raise_for_status()
        return response

    def _dispatch(self, payload):
        url = urljoin(self.remote_host, "ais/add/")
        return self._authenticate_request("POST", url, data=payload)

    def start_dispatch(self):
        while True:
            try:
                if not self.is_active():
                    time.sleep(5)
                    continue
                data = fetch_data()
                payload = self._ais_to_csv(data)
                if not self.can_send_data(payload):
                    time.sleep(int(get_config_value("interval")))
                    continue
                response = self._dispatch(payload)
                if response.status_code == 200:
                    for id, row in data:
                        timestamp = datetime.now()
                        update_sent_at_timestamp(id, timestamp)
                time.sleep(int(get_config_value("interval")))
            except Exception as e:
                # avoid infinite crash loop
                print(e)
                time.sleep(5)


if __name__ == "__main__":
    dispatcher = Dispatcher()
    dispatcher.start_dispatch()
