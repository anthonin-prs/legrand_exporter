"""Application exporter"""

import os
import time
from prometheus_client import start_http_server, Gauge, Enum, Counter
import requests


class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, polling_interval_seconds=10):
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        # self.current_requests = Gauge(
        #     "app_requests_current", "Current requests")
        # self.pending_requests = Gauge(
        #     "app_requests_pending", "Pending requests")
        # self.total_uptime = Gauge("app_uptime", "Uptime")
        # self.health = Enum("app_health", "Health", states=[
        #                    "healthy", "unhealthy"])
        self.todo_count = Gauge(
            "todo_count", "Current todo elements", ['userid', 'completed'])
        self.todo_done = Gauge(
            "todo_done", "Current todo status", ['todo_id', 'title'])

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            self.fetch()
            print("Gathering")
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """

        # Fetch raw status data from the application
        resp = requests.get(url=f"https://jsonplaceholder.typicode.com/todos")
        status_data = resp.json()

        # Update Prometheus metrics with application metrics
        # self.current_requests.set(status_data["current_requests"])
        # self.pending_requests.set(status_data["pending_requests"])
        # self.total_uptime.set(status_data["total_uptime"])
        # self.health.state(status_data["health"])
        for task in status_data:
            if task["completed"] == False:
                self.todo_count.labels(
                    completed='false', userid=task["userId"]).inc()
                self.todo_done.labels(
                    todo_id=task["id"], title=task["title"]).set("1")
            else:
                self.todo_count.labels(
                    completed='true', userid=task["userId"]).inc()
                self.todo_done.labels(
                    todo_id=task["id"], title=task["title"]).set("0")


def main():
    """Main entry point"""

    polling_interval_seconds = int(
        os.getenv("POLLING_INTERVAL_SECONDS", "600"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "8000"))

    app_metrics = AppMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port)
    app_metrics.run_metrics_loop()


if __name__ == "__main__":
    main()
