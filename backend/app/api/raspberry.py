#!/usr/bin/env python3

from flask import Blueprint, jsonify, current_app, request
import datetime
import bson

raspberry = Blueprint("raspberry", __name__)


@raspberry.route("/homestate", methods=["POST"])
def homestate():
    data = request.get_json()

    mongo_db = current_app.config["DATABASE"]
    data["time"] = datetime.datetime.utcnow()
    mongo_db.current_state.insert_one(data)

    return jsonify({"state": "success"}), 200


@raspberry.route("/close", methods=["POST"])
def close():
    data = request.get_json()

    mongo_db = current_app.config["DATABASE"]
    data["time"] = datetime.datetime.utcnow()
    most_recent = mongo_db.current_state.find_one(sort=[("time", -1)])
    mongo_db.current_state.delete_many({})
    mongo_db.historic_changes.insert_one(most_recent)

    return jsonify({}), 200


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
