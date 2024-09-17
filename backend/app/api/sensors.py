#!/usr/bin/env python3

from flask import Blueprint, jsonify, current_app

from app.services.socket_service import get_house_state_from_socket


sensors = Blueprint("sensors", __name__)


# TODO
@sensors.route("/sensores", methods=["GET"])
def sensores():
    house_state = get_house_state_from_socket()
    return (
        jsonify(
            {
                "ac": house_state.get("ac"),
                "alarma": house_state.get("alarm"),
                "luces": house_state.get("lights"),
                "invernadero": house_state.get("water_pump"),
            }
        ),
        200,
    )
