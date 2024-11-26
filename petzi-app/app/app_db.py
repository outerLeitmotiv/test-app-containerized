from .models import db, WebhookEvent


def init_db(app):
    with app.app_context():
        print("Initializing database...")
        db.create_all()
        print("Database initialized.")


def process_data(app, data):
    with app.app_context():
        print("Processing data...")
        event = WebhookEvent(data)
        db.session.add(event)
        db.session.commit()
