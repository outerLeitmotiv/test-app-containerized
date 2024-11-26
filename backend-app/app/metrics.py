from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR, GC_COLLECTOR
from flask import Response

# Unregister default collectors
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(GC_COLLECTOR)

# Define metrics
webhook_requests_total = Counter(
    'webhook_requests_total',
    'Total number of webhook requests processed',
    ['status']  # success, error
)

webhook_processing_time = Histogram(
    'webhook_processing_time_seconds',
    'Time spent processing webhook requests',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

webhook_payload_size = Counter(
    'webhook_payload_size_bytes',
    'Total size of webhook payloads received',
)

def metrics_endpoint():
    """Endpoint that exposes metrics in the Prometheus format"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)