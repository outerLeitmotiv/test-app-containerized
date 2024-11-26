import logging
import pika
import json
import threading
import queue
import time
import os
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sse")

class RabbitMQConnection:
    def __init__(self, max_retries=5, retry_delay=5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None

    def connect(self):
        """Establish connection to RabbitMQ with retry logic"""
        retries = 0
        while retries < self.max_retries:
            try:
                host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
                port = int(os.getenv('RABBITMQ_PORT', '5672'))
                
                parameters = pika.ConnectionParameters(
                    host=host,
                    port=port,
                    connection_attempts=3,
                    retry_delay=2,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue='petzi')
                logger.info("Successfully connected to RabbitMQ")
                return True
                
            except pika.exceptions.AMQPConnectionError as error:
                retries += 1
                if retries == self.max_retries:
                    logger.error(f"Failed to connect to RabbitMQ after {self.max_retries} attempts: {error}")
                    return False
                logger.warning(f"Failed to connect to RabbitMQ. Attempt {retries}/{self.max_retries}. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

    def close(self):
        """Safely close the RabbitMQ connection"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.stop_consuming()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")

def stream_messages():
    message_queue = queue.Queue()
    running = threading.Event()
    running.set()

    def consume_messages():
        rabbitmq = RabbitMQConnection()
        
        while running.is_set():
            try:
                if not rabbitmq.connect():
                    logger.error("Failed to connect to RabbitMQ. Retrying in 5 seconds...")
                    time.sleep(5)
                    continue

                def callback(ch, method, properties, body):
                    try:
                        decoded_message = body.decode()
                        logger.info(f"Received message from queue: {decoded_message}")
                        message_queue.put(decoded_message)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")

                rabbitmq.channel.basic_consume(
                    queue='petzi',
                    on_message_callback=callback,
                    auto_ack=True
                )

                while running.is_set():
                    try:
                        # Process events with a timeout to allow checking running status
                        rabbitmq.connection.process_data_events(time_limit=1)
                    except pika.exceptions.AMQPError as e:
                        logger.error(f"AMQP Error: {e}")
                        break
                    except Exception as e:
                        logger.error(f"Unexpected error in consume_messages: {e}")
                        break

            except Exception as e:
                logger.error(f"Error in consumer thread: {e}")
                time.sleep(5)  # Wait before retry
            finally:
                rabbitmq.close()

    consumer_thread = threading.Thread(target=consume_messages)
    consumer_thread.daemon = True  # Make thread daemon so it exits when main thread exits
    consumer_thread.start()

    try:
        while True:
            try:
                if not message_queue.empty():
                    message = message_queue.get()
                    yield f"data: {json.dumps({'message': message})}\n\n"
                else:
                    # Send heartbeat every second to keep connection alive
                    time.sleep(1)
                    yield f":heartbeat\n\n"
            except Exception as e:
                logger.error(f"Error in message streaming: {e}")
                time.sleep(1)  # Prevent tight loop in case of repeated errors

    except GeneratorExit:
        logger.info("SSE connection closed by client")
        running.clear()
        consumer_thread.join(timeout=5)  # Wait up to 5 seconds for consumer thread to finish