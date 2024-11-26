import os
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from . import app_db, rabbitmq
from .models import db
from .routes import init_app_routes
from .metrics import metrics_endpoint


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    load_dotenv()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.add_url_rule('/metrics', 'metrics', metrics_endpoint)

    db.init_app(app)
    app_db.init_db(app)
    init_app_routes(app)

    return app
