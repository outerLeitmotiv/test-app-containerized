import json
import time
from flask import request, jsonify, Response, stream_with_context
from .validation import is_request_valid
from .app_db import process_data
from .rabbitmq import sending_message
from .sse import stream_messages
from .models import db, WebhookEvent
from .metrics import webhook_requests_total, webhook_processing_time, webhook_payload_size

def init_app_routes(app):
    @app.route('/webhook', methods=['POST'])
    def webhook():
        start_time = time.time()
        
        if not is_request_valid(request):
            webhook_requests_total.labels(status='error').inc()
            return jsonify({'error': 'Invalid request'}), 200
            
        try:
            data = request.get_json()
            # Track payload size
            webhook_payload_size.inc(len(json.dumps(data).encode('utf-8')))
        except Exception as e:
            app.logger.error(f"Error in parsing request data: {e}")
            webhook_requests_total.labels(status='error').inc()
            return jsonify({'error': 'Invalid JSON data'}), 200

        process_data(app, data)
        
        try:
            sending_message(data)
            app.logger.info("Message successfully sent to RabbitMQ.")
            webhook_requests_total.labels(status='success').inc()
            webhook_processing_time.observe(time.time() - start_time)
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            app.logger.error(f"Error in sending message: {e}")
            webhook_requests_total.labels(status='error').inc()
            return jsonify({'error': 'Error sending message to RabbitMQ'}), 200

    @app.route('/events')
    def sse():
        try:
            return Response(
                stream_with_context(stream_messages()), 
                content_type='text/event-stream'
            )
        except Exception as e:
            app.logger.error(f"Error in streaming messages: {e}")
            return jsonify({'error': 'Error streaming messages'}), 500

    @app.route('/api/store-message', methods=['POST'])
    def store_message():
        message_data = request.json.get('message')
        if message_data:
            new_message = WebhookEvent(data=message_data)
            db.session.add(new_message)
            db.session.commit()
            return jsonify({'status': 'success'}), 200
        return jsonify({'error': 'No message provided'}), 400

    @app.route('/api/get-messages', methods=['GET'])
    def get_messages():
        messages = WebhookEvent.query.all()
        formatted_messages = []
        for message in messages:
            message_data = json.loads(message.data)
            if 'details' in message_data and 'ticket' in message_data['details']:
                formatted_messages.append(message_data['details']['ticket'])
        return jsonify(formatted_messages)