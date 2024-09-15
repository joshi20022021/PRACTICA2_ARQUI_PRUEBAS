#!/usr/bin/env python3

from flask import Blueprint, jsonify, current_app

from app.services.socket_service import (
    get_house_state_from_socket,
    send_light_command_to_socket,
)


actuators = Blueprint("actuators", __name__)


# TODO
@actuators.route("/luces", methods=["POST"])
def luces():
    print("UN ANTES")
    house_state = get_house_state_from_socket()
    print("UN DESPUES")

    current_light_state = house_state.get("lights")
    if current_light_state == "on":
        new_light_state = "off"
    else:
        new_light_state = "on"

    send_light_command_to_socket(new_light_state)

    return jsonify({"luces": new_light_state}), 200


# TODO
@actuators.route("/alarma", methods=["POST"])
def alarma():
    return jsonify({"alarma": True}), 200


# TODO
@actuators.route("/invernadero", methods=["POST"])
def invernadero():
    return jsonify({"invernadero": True}), 200
