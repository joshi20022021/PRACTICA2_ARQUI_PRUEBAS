from enum import Enum
import datetime


class HouseStates(Enum):
    PASSWORD = 1
    NORMAL = 2
    BLOCKED = 3


class SensorStates:
    OFF = "off"
    ON = "on"


class LightsChanger(Enum):
    SENSOR = "sensor"
    API = "api"
    SWITCH = "switch"


class SmartHomeState:
    def __init__(
        self,
        temp: float = 0.0,
        humidity: float = 0.0,
        smoke: bool = False,
        light: float = 0.0,
    ):
        self._message: list = ["", ""]

        self._temp = temp
        self.ac: str = SensorStates.OFF
        if self._temp > 27:
            self.ac = SensorStates.ON

        self._humidity = humidity
        self.water_pump = SensorStates.OFF
        self._smoke = smoke
        self.alarm: str = SensorStates.OFF
        if self._smoke:
            self.alarm = SensorStates.ON

        self._light_sensor = light
        self.light = SensorStates.OFF
        if self._light_sensor > 1000:
            self.light = SensorStates.ON
        self._success: list = []
        self._failure: list = []

    def to_dict(self) -> dict:
        return {
            "light_sensor": self._light_sensor,
            "lights": self.light,
            "smoke": self._smoke,
            "alarm": self.alarm,
            "temp_sensor": self._temp,
            "ac": self.ac,
            "humidity": self._humidity,
            "water_pump": self.water_pump,
            "time": "",
            "success": self._success,
            "failure": self._failure,
        }

    @property
    def success(self):
        return self._success

    @success.setter
    def success(self, date):
        self._success.append(date)

    @property
    def failure(self):
        return self._failure

    @failure.setter
    def failure(self, date):
        self._failure.append(date)

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, new_message: str):
        first = new_message[0:16]
        second = new_message[16:32]
        self._message = [first, second]

    @property
    def temp(self):
        return self._temp

    @temp.setter
    def temp(self, new_temp: float):
        self._temp = new_temp
        if self._temp > 27:
            self.ac = SensorStates.ON
        else:
            self.ac = SensorStates.OFF

    @property
    def humidity(self):
        return self._humidity

    @humidity.setter
    def humidity(self, new_humidity: float):
        self._humidity = new_humidity

    @property
    def smoke(self):
        return self._smoke

    @smoke.setter
    def smoke(self, new_smoke: bool):
        self._smoke = new_smoke

    @property
    def light_sensor(self):
        return self._light_sensor

    @light_sensor.setter
    def light_sensor(self, new_light: float):
        self._light_sensor = new_light
        if self._light_sensor > 1000:
            self.light = SensorStates.ON
        else:
            self.light = SensorStates.OFF
