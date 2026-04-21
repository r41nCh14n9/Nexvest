"""Simple Prometheus exporter example for agent metrics.

This is a tiny Flask app exposing /metrics for Prometheus to scrape.
It is a minimal example — in production use a proper WSGI server.
"""
from flask import Flask, Response
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Example metrics
AGENT_REQUESTS = Counter("agent_requests_total", "Total agent requests")
LOOP_DETECTIONS = Counter("agent_loop_detections_total", "Detected loops")
LATENCY_MS = Gauge("agent_latency_ms", "Request latency ms")


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/simulate")
def simulate():
    # Example: increment metrics to demonstrate scraping
    AGENT_REQUESTS.inc()
    LOOP_DETECTIONS.inc(0)
    LATENCY_MS.set(50)
    return "ok\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
