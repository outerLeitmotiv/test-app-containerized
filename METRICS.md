# Custom Metrics Implementation with cAdvisor

## 1. Prometheus Client Setup

Ensure the appropriate Prometheus client is used. This will expose metrics that Prometheus can scrape.

```plaintext
# backend-app/requirements.txt
prometheus-client==0.19.0
```

## 2. Metrics Definition

Define custom metrics in the application code:

```python
# backend-app/app/metrics.py
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR, GC_COLLECTOR
from flask import Response

# Remove default collectors
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(GC_COLLECTOR)

# Define custom metrics
webhook_requests_total = Counter(
    'webhook_requests_total',
    'Total number of webhook requests processed',
    ['status']
)

webhook_processing_time = Histogram(
    'webhook_processing_time_seconds',
    'Time spent processing webhook requests',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

webhook_payload_size = Counter(
    'webhook_payload_size_bytes',
    'Total size of webhook payloads received'
)

# Metrics endpoint
def metrics_endpoint():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
```

## 3. cAdvisor Configuration

Configure cAdvisor to monitor Docker containers:

```yaml
# docker-compose.yml
cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.47.2
    container_name: cadvisor
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    command:
      - --docker_only=true
      - --housekeeping_interval=30s
    ports:
      - "8081:8080"
    networks:
      - app-network
```

## 4. Prometheus Setup

Add Prometheus to scrape metrics from both the application and cAdvisor:

```yaml
# docker-compose.yml
prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - app-network
```

Configure Prometheus scraping:

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'webhook'
    static_configs:
      - targets: ['webhook:5000']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

## 5. Metrics Access Points

- Application metrics: `http://localhost:5000/metrics`
- cAdvisor interface: `http://localhost:8081`
- Prometheus interface: `http://localhost:9090`

## 6. Verification

Test the metrics pipeline:

```bash
# Generate test data
python3 simulator.py http://localhost:5000/webhook mysecretkey --count 5

# Check raw metrics
curl http://localhost:5000/metrics

# Sample output:
# HELP webhook_requests_total Total number of webhook requests processed
# TYPE webhook_requests_total counter
webhook_requests_total{status="success"} 5
```

Check in Prometheus UI:

1. Go to `http://localhost:9090`
2. Query: `webhook_requests_total`
