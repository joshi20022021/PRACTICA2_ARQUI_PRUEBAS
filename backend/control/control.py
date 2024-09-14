#!/usr/bin/env python3

# TODO implement real logic here


import random
import typing


def get_sensor_data(sensor_id) -> dict:
    # Return simulated sensor data (e.g., temperature, light)
    return {"sensor_id": sensor_id, "value": random.uniform(20.0, 30.0)}


# Simulate actuator control (e.g., turn on/off air conditioning)
def control_actuator(actuator_id, state) -> dict:
    # state is either "on" or "off"
    print(f"Actuator {actuator_id} turned {state}")
    return {"actuator_id": actuator_id, "state": state}
