# Custom Metrics POC with cAdvisor

## Introduction

This proof of concept demonstrates the implementation of custom metrics using cAdvisor in a Flask-based web application. The application handles webhooks and exposes custom metrics that can be scraped by Prometheus, making it ideal for monitoring webhook performance and behavior.

## Overview

This POC integrates PostgreSQL for data storage, RabbitMQ for message queuing, and a Vue.js frontend. It's containerized using Docker and showcases how to implement and expose custom metrics in a microservices architecture.

## Features

- **Custom Metrics Monitoring**: Integrated with cAdvisor for monitoring webhook performance metrics
- **Real-Time Data Processing**: Webhook handling with PostgreSQL storage and RabbitMQ queuing
- **Vue.js Dashboard**: Dynamic visualization of webhook data
- **Docker Containerization**: Ensures consistent deployment and testing

### Installation

Clone the repository and set up the project:

```sh
git clone https://github.com/YOUR_USERNAME/cadvisor-metrics-poc
cd cadvisor-metrics-poc
docker-compose up --build
```

### Usage

#### Webhook Server

Access the webhook server at `http://localhost:5000/webhook`. It receives and processes POST requests, storing data in PostgreSQL and sending messages to RabbitMQ.

#### Custom Metrics

The application exposes custom metrics at `http://localhost:5000/metrics`. These metrics include:

- `webhook_requests_total`: Counter tracking total webhook requests (success/error)
- `webhook_processing_time_seconds`: Histogram measuring request processing duration
- `webhook_payload_size_bytes`: Counter tracking total size of webhook payloads

Access cAdvisor metrics dashboard at `http://localhost:8081`.

#### Simulator Script

To test the webhook functionality with randomized data:

```sh
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install faker
pip install faker

# Run simulator
python3 petzi_simulator.py http://localhost:5000/webhook mySecretKey

# Send multiple random requests
python3 petzi_simulator.py http://localhost:5000/webhook mySecretKey --count 5
```

#### RabbitMQ Management Interface

Access the management interface at `http://localhost:15672` (default credentials: guest/guest). This interface allows you to monitor queues and messages.

### Development

For local development:

1. Install dependencies:

```sh
pip install -r requirements.txt
```

2. Start the application:

```sh
python3 petzi_webhook.py
```

### Testing

The `petzi_simulator.py` script is available for testing the webhook functionality with randomized data.

```sh
python petzi_simulator.py http://localhost:5000/webhook mySecret
```

### Database Verification

To access and verify data in the PostgreSQL database:

```sh
docker exec -it postgres_db bash
psql -U postgres
SELECT * FROM webhook_event;
```

### SSE Endpoint

Stream messages from RabbitMQ in real-time through Server-Sent Events (SSE) at the endpoint `http://localhost:5000/events`.

### Deployment

The project is fully containerized using Docker, making deployment straightforward and consistent across different environments.

### Metrics Monitoring

Monitor application performance using custom metrics:

1. Access raw metrics: `http://localhost:5000/metrics`
2. View cAdvisor dashboard: `http://localhost:8081`
3. Custom metrics tracked:
   - Request counts and status
   - Processing times
   - Payload sizes

### .env-example

Rename `.env-example` to `.env` and update it with your environment-specific settings.
