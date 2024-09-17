#!/usr/bin/env python3
#
from flask import Blueprint, jsonify, current_app


graphics = Blueprint("graphics", __name__)


@graphics.route("/graficas", methods=["GET"])
def graficas():

    mongo_db = current_app.config["DATABASE"]
    most_recent = mongo_db.historic_changes.find().sort("time", 1)
    temp_list = []
    ac_list = []
    alarm_list = []
    ingreso_list = []
    greenhouse_list = []
    for item in most_recent:
        print(item)
        temp = {"fecha": item["time"], "temp": item["temp_sensor"]}
        temp_list.append(temp)

        ac = {"fecha": item["time"], "activado": item["ac"]}
        ac_list.append(ac)

        alarm = {"fecha": item["time"], "activado": item["alarm"]}
        alarm_list.append(alarm)

        for acceso in item["success"]:
            date, time = acceso.split(" ")
            ingreso_list.append({"fecha": date, "hora": time, "acceso": True})
        for failure in item["failure"]:
            date, time = failure.split(" ")
            ingreso_list.append({"fecha": date, "hora": time, "acceso": False})

        greenhouse = {"fecha": item["time"], "activado": item["water_pump"]}
        greenhouse_list.append(greenhouse)

    return (
        jsonify(
            {
                "temperatura": temp_list,
                "ac": ac_list,
                "alarma": alarm_list,
                "ingreso": ingreso_list,
                "invernadero": greenhouse_list,
            }
        ),
        200,
    )
