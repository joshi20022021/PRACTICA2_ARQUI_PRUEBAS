#!/usr/bin/env python3
from flask import Blueprint, jsonify, current_app, request


lcd = Blueprint("lcd", __name__)


# TODO
@lcd.route("/mensajes", methods=["POST"])
def mensajes():
    data = request.get_json()
    return jsonify({"mensaje_recibido": data["mensaje"]}), 200
