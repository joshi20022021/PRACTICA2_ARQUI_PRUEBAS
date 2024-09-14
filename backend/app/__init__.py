#!/usr/bin/env python3
import os
from flask import Flask
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv


load_dotenv()


def create_app():
    app = Flask(__name__)

    # load .env variables
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    mongo_uri = os.getenv("MONGO_URI")
    pem_path = os.getenv("MONGO_PEM_PATH")

    # connect to mongodb using certificate
    client = MongoClient(
        mongo_uri, tls=True, tlsCertificateKeyFile=pem_path, server_api=ServerApi("1")
    )
    app.db = client["proyect-1"]

    from app.api.v1 import api_v1

    app.register_blueprint(api_v1, url_prefix="/api/")

    return app
