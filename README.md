# Containerized Microservices POC

## Introduction

This proof of concept demonstrates a containerized microservices architecture with custom metrics monitoring. The application simulates an integration with PETZI's webhook system.

### About PETZI

PETZI represents concert venues and festivals operating on a non-profit basis. The federation facilitates event management and ticket sales through its digital platform. Our POC simulates webhook interactions similar to PETZI's system, which handles real-time event updates.

## Architecture Overview

The POC implements a complete microservices stack:

- **Backend**: Flask-based webhook service with custom metrics
- **Frontend**: Vue.js dashboard for data visualization
- **Database**: PostgreSQL for event data storage
- **Message Broker**: RabbitMQ for event message queuing
- **Monitoring**: cAdvisor for container and custom metrics monitoring

## Features

- **Custom Metrics Monitoring**: Integrated with cAdvisor for monitoring webhook performance metrics
- **Real-Time Data Processing**: Webhook handling with PostgreSQL storage and RabbitMQ queuing
- **Vue.js Dashboard**: Dynamic visualization of webhook data
- **Docker Containerization**: Ensures consistent deployment and testing

## Installation and Setup

### Clone the repository

```sh
git clone https://github.com/outerLeitmotiv/test-app-containerized
cd test-app-containerized
```

### Configure environment

```sh
# Copy example environment file
cp .env-example .env

# Environment variables needed:
DATABASE_URI=postgresql://postgres:mysecretpassword@db:5432/postgres
SECRET_KEY=mysecretkey
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
```

### Start the services

```sh
docker-compose up --build
```

## Service Endpoints

### Webhook Server

- URL: `http://localhost:5000/webhook`
- Purpose: Receives and processes POST requests
- Functions: Stores data in PostgreSQL and sends messages to RabbitMQ

### Custom Metrics

Access custom metrics at `http://localhost:5000/metrics`
Metrics exposed:

- `webhook_requests_total`: Counter tracking total webhook requests (success/error)
- `webhook_processing_time_seconds`: Histogram measuring request processing duration
- `webhook_payload_size_bytes`: Counter tracking total size of webhook payloads

### Monitoring Dashboards

- cAdvisor: `http://localhost:8081`
- RabbitMQ Management: `http://localhost:15672` (credentials: guest/guest)
- Vue.js Frontend: `http://localhost:8080`

## Testing

### Simulator Setup

The simulator requires a Python virtual environment:

```sh
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements (from root directory)
pip install -r requirements.txt

# Run simulator
python3 simulator.py http://localhost:5000/webhook mysecretkey

# Send multiple requests
python3 simulator.py http://localhost:5000/webhook mysecretkey --count 5
```

Note: The project contains two separate requirements.txt files:

- `/backend-app/requirements.txt`: Used by Docker for the backend service
- `/requirements.txt`: Used for running the simulator locally

### Database Verification

```sh
docker exec -it postgres_db bash
psql -U postgres
SELECT * FROM webhook_event;
```

### Event Streaming

The application supports Server-Sent Events (SSE) for real-time message streaming:

- Endpoint: `http://localhost:5000/events`
- Purpose: Stream messages from RabbitMQ in real-time

## Metrics Monitoring

Monitor application performance through:

1. Raw metrics: `http://localhost:5000/metrics`
2. cAdvisor dashboard: `http://localhost:8081`
3. Custom metrics tracked:
   - Request counts and status
   - Processing times
   - Payload sizes

## Development

The project is designed as a foundation for:

- Testing microservices patterns
- Implementing new services
- Experimenting with monitoring solutions
- Learning containerized application deployment

## Documentation

- See [METRICS.md](METRICS.md) for detailed information about metrics implementation
- Check individual service directories for specific documentation

## Deployment

The project is fully containerized using Docker, making deployment straightforward and consistent across different environments. All necessary services are defined in docker-compose.yml.

## License

MIT License