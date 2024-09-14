#!/usr/bin/env python3

from flask import Blueprint, jsonify, current_app

from app.services.socket_service import get_house_state_from_socket


sensors = Blueprint("sensors", __name__)


# TODO
@sensors.route("/sensores", methods=["GET"])
def sensores():
    try:
        print(get_house_state_from_socket())
    except FileNotFoundError:
        print("Smart Home isn't running!!!")
    return jsonify({"hola": 5}), 200
