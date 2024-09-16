from enum import Enum


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
        message: str = "",
        temp: float = 0.0,
        humidity: float = 0.0,
        smoke: float = 0.0,
        light: float = 0.0,
    ):
        self.message = message

        self._temp = temp
        self.ac: str = SensorStates.OFF
        if self._temp > 27:
            self.ac = SensorStates.ON

        self._humidity = humidity
        self.water_pump = SensorStates.OFF
        if self._humidity < 500:
            self.water_pump = SensorStates.ON
        self._smoke = smoke
        self.alarm: str = SensorStates.OFF
        if self._smoke > 1000:
            self.alarm = SensorStates.ON

        self._light_sensor = light
        self.light = SensorStates.OFF
        if self._light_sensor > 1000:
            self.light = SensorStates.ON

    @property
    def temp(self):
        return self.temp

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
        if self._humidity < 500:
            self.water_pump = SensorStates.ON

    @property
    def smoke(self):
        return self._smoke

    @smoke.setter
    def smoke(self, new_smoke: float):
        self._smoke = new_smoke
        if self._smoke > 1000:
            self.alarm = SensorStates.ON
        else:
            self.alarm = SensorStates.OFF

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
