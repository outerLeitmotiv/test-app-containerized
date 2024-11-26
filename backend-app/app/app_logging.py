import logging
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    file_handler = RotatingFileHandler('flask_app.log', maxBytes=1000000, backupCount=10)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
