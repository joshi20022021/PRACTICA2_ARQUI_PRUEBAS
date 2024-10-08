#!/usr/bin/env python3

import datetime
from flask import Blueprint, jsonify, current_app

from app.services.socket_service import (
    get_house_state_from_socket,
    send_alarm_command_to_socket,
    send_greenhouse_command_to_socket,
    send_light_command_to_socket,
)


actuators = Blueprint("actuators", __name__)


@actuators.route("/luces", methods=["POST"])
def luces():
    house_state = get_house_state_from_socket()

    current_light_state = house_state.get("lights")
    new_light_state = state_changer(current_light_state)

    send_light_command_to_socket(new_light_state)
    house_state = get_house_state_from_socket()

    mongo_db = current_app.config["DATABASE"]
    house_state["time"] = datetime.datetime.utcnow()
    mongo_db.current_state.insert_one(house_state)
    mongo_db.historic_changes.insert_one(house_state)

    return jsonify({"luces": new_light_state}), 200


@actuators.route("/alarma", methods=["POST"])
def alarma():
    house_state = get_house_state_from_socket()

    current_alarm_state = house_state.get("alarm")
    new_alarm_state = state_changer(current_alarm_state)

    send_alarm_command_to_socket(new_alarm_state)
    house_state = get_house_state_from_socket()

    mongo_db = current_app.config["DATABASE"]
    house_state["time"] = datetime.datetime.utcnow()
    mongo_db.current_state.insert_one(house_state)
    mongo_db.historic_changes.insert_one(house_state)

    return jsonify({"alarma": new_alarm_state}), 200


@actuators.route("/invernadero", methods=["POST"])
def invernadero():
    house_state = get_house_state_from_socket()

    current_greenhouse_state = house_state.get("water_pump")
    new_greenhouse_state = state_changer(current_greenhouse_state)

    send_greenhouse_command_to_socket(new_greenhouse_state)
    house_state = get_house_state_from_socket()

    mongo_db = current_app.config["DATABASE"]
    house_state["time"] = datetime.datetime.utcnow()
    mongo_db.current_state.insert_one(house_state)
    mongo_db.historic_changes.insert_one(house_state)

    return jsonify({"invernadero": new_greenhouse_state}), 200


def state_changer(state):
    if state == "on":
        return "off"
    else:
        return "on"
