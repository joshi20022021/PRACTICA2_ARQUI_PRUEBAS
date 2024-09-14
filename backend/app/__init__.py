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
        DATABASE=mongo_client["smart_home"],
    )

    return app
