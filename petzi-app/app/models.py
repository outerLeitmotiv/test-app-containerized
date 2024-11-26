from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


class WebhookEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False)

    def __init__(self, data):
        self.data = json.dumps(data)
