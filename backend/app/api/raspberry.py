#!/usr/bin/env python3

from flask import Blueprint, jsonify, current_app, request


raspberry = Blueprint("raspberry", __name__)


# TODO
# send to mongo DB
@raspberry.route("/luces", methods=["POST"])
def luces():
    data = request.get_json()

    return jsonify({"luces": data["light"]}), 200


# TODO
# send to mongo db
@raspberry.route("/alarma", methods=["POST"])
def alarma():
    data = request.get_json()

    return jsonify({"alarm": data["alarm"]}), 200


# TODO
# send to mongodb
@raspberry.route("/invernadero", methods=["POST"])
def invernadero():
    data = request.get_json()

    return jsonify({"invernadero": data["water_pump"]}), 200
