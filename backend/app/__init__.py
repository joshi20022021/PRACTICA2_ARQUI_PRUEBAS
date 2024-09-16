#!/usr/bin/env python3
import os
from flask import Flask
from pymongo import MongoClient, mongo_client
from pymongo.server_api import ServerApi
from dotenv import load_dotenv


load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=os.getenv("SECRET_KEY"))

    # load .env variables
    mongo_uri = os.getenv("MONGO_URI")
    pem_path = os.getenv("MONGO_PEM_PATH")
    # connect to mongodb using certificate
    mongo_client = MongoClient(
        mongo_uri, tls=True, tlsCertificateKeyFile=pem_path, server_api=ServerApi("1")
    )

    app.config.from_mapping(
        DATABASE_CLIENT=mongo_client,
        DATABASE=mongo_client["smart-home"],
    )

    from app.api.sensors import sensors
    from app.api.actuators import actuators
    from app.api.graphics import graphics
    from app.api.lcd import lcd
    from app.api.raspberry import raspberry

    app.register_blueprint(sensors)
    app.register_blueprint(actuators)
    app.register_blueprint(graphics)
    app.register_blueprint(lcd)
    app.register_blueprint(raspberry, url_prefix="/raspberry")

    return app
