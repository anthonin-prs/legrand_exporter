"""Application exporter"""

import os
import time
import json
from prometheus_client import start_http_server, Gauge, Enum, Counter
import requests


class LegrandMetrics:
    endpoint = os.environ["ENDPOINT_URL"]
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    access_token = os.environ["ACCESS_TOKEN"]
    refresh_token = os.environ["REFRESH_TOKEN"]
    home_id = os.environ["HOME_ID"]
    metadata = {}

    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, polling_interval_seconds=10):
        self.polling_interval_seconds = polling_interval_seconds
        with open('/app/src/metadata.json') as file:
            self.metadata = json.load(file)

        self.module_device_info = Gauge(
            "module_device_info", "Module informations status", ['device', 'name', 'tag', 'network_status', 'type', 'source'])
        self.module_power_status = Gauge(
            "module_power_status", "Module turned on or off", ['device', 'name', 'tag', 'type'])
        self.module_power_consumption = Gauge(
            "module_power_consumption", "Power consuption of module", ['device', 'name', 'tag', 'type'])
        self.room_temperature = Gauge(
            "room_temperature", "Temperature sensor", ['room_id'])
        self.room_humidity = Gauge(
            "room_humidity", "Humidity sensor", ['room_id'])

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            if not self.check_token():
                self.refresh_tokens()

            self.fetch()
            print("Gathering")
            time.sleep(self.polling_interval_seconds)

    def check_token(self):
        print("Checking tokens")
        request = requests.get(self.endpoint+"/api/homesdata", headers={
            "Content-Type": "application/json", "Authorization": "Bearer "+self.access_token}, verify=False)
        result = request.json()
        if "error" in result:
            print("KO",result)
            return False
        else:
            print("OK")
            return True

    def refresh_tokens(self):
        print("Refreshing Tokens")
        request_body = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        print("Body",request_body)
        request = requests.post(self.endpoint+"/oauth2/token",
                                data=request_body, verify=False)
        print("Result",request.json())
        os.environ["access_token"] = request.json()['access_token']
        os.environ["refresh_token"] = request.json()['refresh_token']
        print("New tokens\n - Access:",os.environ["access_token"],"\n - Refresh:",os.environ["refresh_token"])

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """

        # Fetch raw status data from the application
        resp = requests.get(self.endpoint+"/api/homestatus", headers={
            "Authorization": "Bearer "+self.access_token}, data={"home_id": self.home_id}, verify=False)
        modules = []
        print(resp.json()['body']['home'].keys())
        if modules in resp.json()['body']['home'].keys():
            modules = resp.json()['body']['home']['modules']
        rooms = []
        if rooms in resp.json()['body']['home']:
            rooms = resp.json()['body']['home']['rooms']

        for room in rooms:
            self.room_temperature.labels(
                room_id=room["id"]).set(room['therm_measured_temperature'])
            self.room_humidity.labels(
                room_id=room["id"]).set(room['humidity'])

        for module in modules:
            if "on" in module:
                if module["reachable"]:
                    if module["on"]:
                        self.module_device_info.labels(
                            device=self.metadata[module['id']]['name'],
                            name=self.metadata[module['id']]['name'],
                            tag=self.metadata[module['id']]['tag'],
                            network_status="ONLINE",
                            type=self.metadata[module['id']]['type'],
                            source="Netatmo").set("1")

                        self.module_power_status.labels(
                            device=self.metadata[module['id']]['name'],
                            name=self.metadata[module['id']]['name'],
                            tag=self.metadata[module['id']]['tag'],
                            type=self.metadata[module['id']]['type']).set("1")

                        self.module_power_consumption.labels(
                            device=self.metadata[module['id']]['name'],
                            name=self.metadata[module['id']]['name'],
                            tag=self.metadata[module['id']]['tag'],
                            type=self.metadata[module['id']]['type']).set(str(module['power']))

                    else:
                        self.module_device_info.labels(
                            device=self.metadata[module['id']]['name'],
                            name=self.metadata[module['id']]['name'],
                            tag=self.metadata[module['id']]['tag'],
                            network_status="ONLINE",
                            type=self.metadata[module['id']]['type'],
                            source="Netatmo").set("1")

                        self.module_power_status.labels(
                            device=self.metadata[module['id']]['name'],
                            name=self.metadata[module['id']]['name'],
                            tag=self.metadata[module['id']]['tag'],
                            type=self.metadata[module['id']]['type']).set("0")

                else:
                    self.module_device_info.labels(
                        device=self.metadata[module['id']]['name'],
                        name=self.metadata[module['id']]['name'],
                        tag=self.metadata[module['id']]['tag'],
                        network_status="OFFLINE",
                        type=self.metadata[module['id']]['type'],
                        source="Netatmo").set("1")


def main():
    """Main entry point"""

    polling_interval_seconds = int(
        os.getenv("POLLING_INTERVAL_SECONDS", "600"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "8000"))

    app_metrics = LegrandMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port)
    app_metrics.run_metrics_loop()


if __name__ == "__main__":
    main()
