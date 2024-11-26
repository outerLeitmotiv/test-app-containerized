import pika
import time
import os
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def get_rabbitmq_connection(max_retries=5, retry_delay=5):
    """Create a RabbitMQ connection with retry logic"""
    retries = 0
    while retries < max_retries:
        try:
            # Get connection parameters from environment or use defaults
            host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
            port = int(os.getenv('RABBITMQ_PORT', 5672))
            
            parameters = pika.ConnectionParameters(
                host=host,
                port=port,
                connection_attempts=3,
                retry_delay=2,
                heartbeat=600
            )
            
            connection = pika.BlockingConnection(parameters)
            logger.info("Successfully connected to RabbitMQ")
            return connection
            
        except pika.exceptions.AMQPConnectionError as error:
            retries += 1
            if retries == max_retries:
                logger.error(f"Failed to connect to RabbitMQ after {max_retries} attempts")
                raise
            logger.warning(f"Failed to connect to RabbitMQ. Attempt {retries}/{max_retries}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

def with_rabbitmq_connection(f):
    """Decorator to handle RabbitMQ connection"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        connection = get_rabbitmq_connection()
        try:
            return f(connection, *args, **kwargs)
        finally:
            try:
                connection.close()
            except Exception:
                pass
    return wrapper
