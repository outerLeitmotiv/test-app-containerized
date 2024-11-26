# **Custom Metrics Implementation with cAdvisor**

## **1. Prometheus Client Setup**

Ensure the appropriate Prometheus client is used. This will expose metrics that Prometheus can scrape.

```plaintext
# backend-app/requirements.txt
prometheus-client==0.19.0
```

---

## **2. Metrics Definition**

Define custom metrics in the application code. The following example shows how to define metrics for tracking webhook requests, processing time, and payload size:

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

---

## **3. Metrics Integration in Webhook Route**

Integrate the custom metrics into the application logic (e.g., for webhook handling):

```python
# backend-app/app/routes.py
@app.route('/webhook', methods=['POST'])
def webhook():
    start_time = time.time()
    
    try:
        data = request.get_json()
        webhook_payload_size.inc(len(json.dumps(data).encode('utf-8')))
        
        # Process webhook...
        
        webhook_requests_total.labels(status='success').inc()
        webhook_processing_time.observe(time.time() - start_time)
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        webhook_requests_total.labels(status='error').inc()
        webhook_processing_time.observe(time.time() - start_time)
        return jsonify({'error': str(e)}), 500
```

---

## **4. cAdvisor Configuration**

Set up cAdvisor to monitor Docker containers using the following configuration in `docker-compose.yml`:

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
    restart: unless-stopped
```

---

## **5. Exposed Metrics**

The application and cAdvisor will expose metrics via HTTP endpoints that Prometheus can scrape:

- **Application Metrics**: Accessible via `http://localhost:5000/metrics`.
- **cAdvisor Metrics**: Accessible via `http://localhost:8081`.

### **Sample Metrics Output**

**Application Metrics**:

```plaintext
# HELP webhook_requests_total Total number of webhook requests processed
# TYPE webhook_requests_total counter
webhook_requests_total{status="success"} 42

# HELP webhook_processing_time_seconds Time spent processing webhook requests
# TYPE webhook_processing_time_seconds histogram
webhook_processing_time_seconds_bucket{le="0.01"} 10
```
