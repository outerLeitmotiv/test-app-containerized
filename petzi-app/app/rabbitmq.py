import pika
import json


def sending_message(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='petzi')

    event_type = data.get('event')
    details = data.get('details', {})

    if event_type == 'ticket_created':
        message = f"Ticket Created: {json.dumps(details)}"
    elif event_type == 'ticket_updated':
        cancellation_reason = details.get('ticket', {}).get('cancellationReason', 'unknown')
        message = f"Ticket Updated: Reason - {cancellation_reason}, Details: {json.dumps(details)}"
    else:
        message = f"Unknown Event: {json.dumps(data)}"

    channel.basic_publish(exchange='', routing_key='petzi', body=message)
    print(f" [x] Sent message to 'petzi' queue: {message}")

    connection.close()


def receive_message():
    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='petzi')
    channel.basic_consume(queue='petzi', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
