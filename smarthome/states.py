from enum import Enum


class HouseStates(Enum):
    PASSWORD = 1
    NORMAL = 2
    BLOCKED = 3


class SensorStates:
    OFF = "off"
    ON = "on"


class SmartHomeState:
    def __init__(
        self,
        message: str = "",
        temp: float = 0.0,
        humidity: float = 0.0,
        smoke: float = 0.0,
        light: float = 0.0,
    ):
        self.message = message

        self.temp = temp
        self.ac: str = SensorStates.OFF
        if self.temp > 27:
            self.ac = SensorStates.ON

        self.humidity = humidity
        self.smoke = smoke
        self.alarm: str = SensorStates.OFF
        if self.smoke > 1000:
            self.alarm = SensorStates.ON

        self.light_sensor = light
        self.light = SensorStates.OFF
        if self.light_sensor > 1000:
            self.light = SensorStates.ON
