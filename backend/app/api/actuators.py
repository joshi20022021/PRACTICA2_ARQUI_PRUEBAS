#!/usr/bin/env python3

from flask import Blueprint, jsonify, current_app


actuators = Blueprint("actuators", __name__)


# TODO
@actuators.route("/luces", methods=["POST"])
def luces():
    return jsonify({"luces": False}), 200


# TODO
@actuators.route("/alarma", methods=["POST"])
def alarma():
    return jsonify({"alarma": True}), 200


# TODO
@actuators.route("/invernadero", methods=["POST"])
def invernadero():
    return jsonify({"invernadero": True}), 200
