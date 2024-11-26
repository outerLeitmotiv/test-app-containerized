from datetime import datetime
import hashlib
import hmac
import os


def is_request_valid(req):
    secret = os.getenv('SECRET_KEY').encode()

    received_sig_full = req.headers.get('Petzi-Signature')
    signature_parts = dict(part.split('=') for part in received_sig_full.split(','))

    body_to_sign = f'{signature_parts["t"]}.{req.data.decode()}'.encode()
    expected_sig = hmac.new(secret, body_to_sign, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature_parts['v1'], expected_sig):
        return False

    time_delta = (datetime.now() -
                  datetime.fromtimestamp(int(signature_parts['t'])))
    if time_delta.total_seconds() > 30:
        return False

    return True
