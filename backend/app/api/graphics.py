#!/usr/bin/env python3
#
from flask import Blueprint, jsonify, current_app


graphics = Blueprint("graphics", __name__)


@graphics.route("/graficas", methods=["GET"])
def graficas():
    return (
        jsonify(
            {
                "grafica1": "imagen1.jpeg",
                "grafica2": "imagen2.jpeg",
                "grafica3": "imagen3.jpeg",
            }
        ),
        200,
    )
