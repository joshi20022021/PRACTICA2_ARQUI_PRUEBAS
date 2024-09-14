#!/usr/bin/env python3

from flask import Blueprint, jsonify, current_app


sensors = Blueprint("sensors", __name__)


# TODO
@sensors.route("/sensores", methods=["GET"])
def sensores():
    return jsonify({"hola": 5}), 200
