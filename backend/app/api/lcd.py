#!/usr/bin/env python3
from flask import Blueprint, jsonify, current_app, request

from app.api.actuators import state_changer
from app.services.socket_service import (
    get_house_state_from_socket,
    send_alarm_command_to_socket,
    send_message_to_socket,
)


lcd = Blueprint("lcd", __name__)


# TODO
@lcd.route("/mensajes", methods=["POST"])
def mensajes():
    data = request.get_json()
    send_message_to_socket(data["mensaje"])
    return jsonify({"message": "Message received: " + data["mensaje"]}), 200
