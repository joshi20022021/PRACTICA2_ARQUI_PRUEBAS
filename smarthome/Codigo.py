from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from socket_server import handle_command_socket, handle_state_socket
from states import HouseStates, LightsChanger, SensorStates, SmartHomeState

import spidev
import adafruit_dht
import board
import digitalio

import threading
from datetime import datetime
from time import sleep
import requests

# LCD DISPLAY
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

lcd = I2cLcd(1, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Variables para el sensor de luz
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 100000

LUZ_CHANNEL = 0
GAS_CHANNEL = digitalio.DigitalInOut(board.D22)

# Sensor de temp y humedad
DHT11_DEV = adafruit_dht.DHT11(board.D21)

# Configuraciones de pines usando digitalio
LUCES_CASA = [digitalio.DigitalInOut(board.D13)]
SENSOR_LUZ = digitalio.DigitalInOut(board.D6)
ENCENDER_LUCES = digitalio.DigitalInOut(board.D16)
BOTON_AIRE = digitalio.DigitalInOut(board.D17)
ALARMA = digitalio.DigitalInOut(board.D12)
ROCIADORES = digitalio.DigitalInOut(board.D26)
BOTON_RIEGO = digitalio.DigitalInOut(board.D19)
REGADORES = digitalio.DigitalInOut(board.D20)

BOTON_SECCION = digitalio.DigitalInOut(board.D27)
BOTON_ASTERISCO = digitalio.DigitalInOut(board.D24)
BOTON_GRUPO = digitalio.DigitalInOut(board.D4)
BOTON_ENTER = digitalio.DigitalInOut(board.D5)

# Configuración de la dirección de los pines
for pin in LUCES_CASA:
    pin.direction = digitalio.Direction.OUTPUT

SENSOR_LUZ.direction = digitalio.Direction.INPUT
ENCENDER_LUCES.direction = digitalio.Direction.INPUT
BOTON_AIRE.direction = digitalio.Direction.INPUT
BOTON_SECCION.direction = digitalio.Direction.INPUT
BOTON_ASTERISCO.direction = digitalio.Direction.INPUT
BOTON_GRUPO.direction = digitalio.Direction.INPUT
BOTON_ENTER.direction = digitalio.Direction.INPUT
ROCIADORES.direction = digitalio.Direction.OUTPUT
ALARMA.direction = digitalio.Direction.OUTPUT
BOTON_RIEGO.direction = digitalio.Direction.INPUT
REGADORES.direction = digitalio.Direction.OUTPUT


# SmartHomeState
SMARTHOME = SmartHomeState()
ULTIMO_CAMBIO_LUCES: LightsChanger = LightsChanger.SENSOR
API_URL = "http://127.0.0.1:5000/raspberry/"


temp_message_thread = None


def main():
    global temp_message_thread
    # Main program block
    ##################
    # ENCENDER Y APAGAR LUZ CON SENSOR
    password = []

    my_state = MyHouseState()
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d/%m/%Y")
    house_state = ["Temp 27 c", formatted_date]
    SMARTHOME.temp = 27
    new_house_state = house_state.copy()

    lcd_message(house_state[0], house_state[1])

    blocked_thread = None
    temperature_message_thread = None

    intento = 0
    estado_actual_casa = HouseStates.NORMAL

    # BOTON DE LUZ APAGADO
    while True:

        # When is in normal mode
        if estado_actual_casa == HouseStates.NORMAL:
            # new_house_state = sensor_temperatura(formatted_date)

            new_house_state = my_state.new_house_state
            if SMARTHOME.message[0] != "":
                if temp_message_thread != None and temperature_message_thread != None:
                    if (
                        not temp_message_thread.is_alive()
                        and not temperature_message_thread.is_alive()
                    ):
                        temp_message_thread = threading.Thread(
                            target=lcd_temp_message,
                            args=(
                                new_house_state,
                                SMARTHOME.message[0],
                                SMARTHOME.message[1],
                            ),
                        )
                        temp_message_thread.start()
                        sleep(0.5)
                        SMARTHOME.message = ""
                else:
                    temp_message_thread = threading.Thread(
                        target=lcd_temp_message,
                        args=(
                            new_house_state,
                            SMARTHOME.message[0],
                            SMARTHOME.message[1],
                        ),
                    )
                    temp_message_thread.start()
                    sleep(0.5)
                    SMARTHOME.message = ""

            if temperature_message_thread != None and temp_message_thread != None:
                if (
                    not temperature_message_thread.is_alive()
                    and not temp_message_thread.is_alive()
                ):
                    temperature_message_thread = threading.Thread(
                        target=mod_temperature_mesg,
                        args=(my_state, formatted_date),
                    )
                    temperature_message_thread.start()
            else:
                temperature_message_thread = threading.Thread(
                    target=mod_temperature_mesg, args=(my_state, formatted_date)
                )
                temperature_message_thread.start()

            luces_casa(new_house_state)
            sensor_fuego(new_house_state)
            sensor_humedad(new_house_state)
            reset_house_state(
                temp_message_thread, house_state, new_house_state, my_state
            )

            if BOTON_ENTER.value:
                estado_actual_casa = HouseStates.PASSWORD
                lcd_message("Ingrese Password", "***")

        # When is in Blocked mode
        elif estado_actual_casa == HouseStates.BLOCKED:
            new_house_state = my_state.new_house_state
            luces_casa(new_house_state)
            sensor_fuego(new_house_state)
            sensor_humedad(new_house_state)
            if blocked_thread is not None:
                if not blocked_thread.is_alive():
                    estado_actual_casa = HouseStates.NORMAL
                    blocked_thread = None
                    sleep(0.5)
            else:
                blocked_thread = threading.Thread(target=bloquear_casa)
                blocked_thread.start()

        # When is in Password mode
        elif estado_actual_casa == HouseStates.PASSWORD:
            new_house_state = my_state.new_house_state
            luces_casa(new_house_state)
            sensor_fuego(new_house_state)
            sensor_humedad(new_house_state)
            if len(password) < 3:
                password = guardar_botones(password)
            elif len(password) == 3 and BOTON_ENTER.value:

                aceptado = verificar_password(password)
                password = []

                if aceptado:
                    intento = 0

                    temp_message_thread = threading.Thread(
                        target=lcd_temp_message,
                        args=(new_house_state, "Password", "Correcta"),
                    )
                    temp_message_thread.start()
                    estado_actual_casa = HouseStates.NORMAL
                    sleep(0.5)

                else:
                    temp_message_thread = threading.Thread(
                        target=lcd_temp_message,
                        args=(new_house_state, "Password", "Incorrecta"),
                    )
                    intento += 1

                    if intento == 3:
                        estado_actual_casa = HouseStates.BLOCKED
                        intento = 0
                        sleep(0.5)
                    else:
                        estado_actual_casa = HouseStates.NORMAL
                        temp_message_thread.start()
                        sleep(0.5)

            sleep(0.1)

        response = requests.post(API_URL + "homestate", json=SMARTHOME.to_dict())


def sensor_humedad(new_house_state):
    global temp_message_thread

    # print(SMARTHOME.to_dict())
    water_pump_val = True if SMARTHOME.water_pump == "on" else False
    if water_pump_val:

        if temp_message_thread != None:
            if not temp_message_thread.is_alive():
                temp_message_thread = threading.Thread(
                    target=lcd_temp_message,
                    args=(
                        new_house_state,
                        "REGANDO",
                        "INVERNADERO",
                    ),
                )
                temp_message_thread.start()
                sleep(0.5)
        ROCIADORES.value = True
    else:
        ROCIADORES.value = False


SENSOR_FUEGO_REINICIADO = True
LAST_STATE = True


def sensor_fuego(new_house_state):
    global SENSOR_FUEGO_REINICIADO, temp_message_thread, LAST_STATE
    # LOGICA SENSOR FUEGO
    # gas_value = read_adc(GAS_CHANNEL)  # Leer canal 1 (sensor de gas)
    gas_value = not GAS_CHANNEL.value
    SMARTHOME.smoke = gas_value
    # convert_to_volts = lambda x, val: (x * val) / 4096.0
    # gas_voltage = convert_to_volts(gas_value, 5.0)
    # print("VALOR VOLTAGE", gas_voltage)
    # print("VALOR GAS: ", gas_value)
    smart_home: bool = False
    SENSOR_FUEGO_REINICIADO = False
    if SMARTHOME.alarm == "off":
        SENSOR_FUEGO_REINICIADO = True
        smart_home = True
        LAST_STATE = False

    if gas_value and SENSOR_FUEGO_REINICIADO:
        SMARTHOME.smoke = gas_value
        ALARMA.value = True
        SMARTHOME.alarm = "on"
        SENSOR_FUEGO_REINICIADO = False
        SMARTHOME.humidity = 500
        LAST_STATE = True

        if temp_message_thread != None:
            if not temp_message_thread.is_alive():
                temp_message_thread = threading.Thread(
                    target=lcd_temp_message,
                    args=(
                        new_house_state,
                        "ALERTA!!",
                        "FUEGO!!!",
                    ),
                )
                temp_message_thread.start()
                sleep(0.5)
        else:
            temp_message_thread = threading.Thread(
                target=lcd_temp_message,
                args=(
                    new_house_state,
                    "ALERTA!!",
                    "FUEGO!!!",
                ),
            )
            temp_message_thread.start()
            sleep(0.5)
        return
    elif not SENSOR_FUEGO_REINICIADO and LAST_STATE:
        ALARMA.value = True
        return

    ALARMA.value = False


def mod_temperature_mesg(new_house_state, formatted_date):
    # print("#" * 15)
    # print(new_house_state)
    # print("#" * 15)
    new_house_state = sensor_temperatura(formatted_date, new_house_state)


def sensor_temperatura(formatted_date, myhs):
    try:
        temperature = DHT11_DEV.temperature
        humidity = DHT11_DEV.humidity

        if humidity is not None and temperature is not None:
            # print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
            SMARTHOME.temp = temperature
            SMARTHOME.humidity = humidity
            pass
        else:
            print("Failed to get reading. Try again!")
            temperature = "Err"
            humidity = "Err"

    except RuntimeError as error:
        print(f"Error reading DHT11: {error}")
        temperature = "Err"
        humidity = "Err"

    except OverflowError as error:
        print(f"OverflowError: {error}")
        sleep(2)  # Pausa antes de reintentar la lectura
        temperature = "Err"
        humidity = "Err"

    new_house_state = [
        "Temp " + str(temperature) + " C " + str("E" if LUCES_CASA[0].value else "A"),
        formatted_date,
    ]
    myhs.new_house_state = new_house_state
    sleep(2)
    # return new_house_state


def luces_casa(new_house_state):
    global ULTIMO_CAMBIO_LUCES, SMARTHOME, temp_message_thread
    # LOGICA LUCES DE LA CASA
    ENCENDIDAS = ENCENDER_LUCES.value
    light_value = read_adc(LUZ_CHANNEL)  # Leer canal 0 (foto resistencia)
    # print("LUZ CASA: ", light_value)
    light_sensor: bool = False
    if light_value < 500:
        light_sensor = True
    else:
        light_sensor = False

    home_sensor: bool = False
    if SMARTHOME.light == "on":
        home_sensor = True

    estado_actual: bool = LUCES_CASA[0].value

    def actualizar_luces():
        global temp_message_thread
        match ULTIMO_CAMBIO_LUCES:
            case LightsChanger.SENSOR:
                estado_luces = light_sensor
            case LightsChanger.SWITCH:
                estado_luces = ENCENDIDAS
            case LightsChanger.API:
                estado_luces = home_sensor

        LUCES_CASA[0].value = estado_luces
        SMARTHOME.light = "on" if estado_luces else "off"

    if (
        light_sensor != LUCES_CASA[0].value
        and ULTIMO_CAMBIO_LUCES != LightsChanger.SENSOR
    ):
        ULTIMO_CAMBIO_LUCES = LightsChanger.SENSOR
        actualizar_luces()

    # Si cambia el switch
    if (
        ENCENDIDAS != LUCES_CASA[0].value
        and ULTIMO_CAMBIO_LUCES != LightsChanger.SWITCH
    ):
        ULTIMO_CAMBIO_LUCES = LightsChanger.SWITCH
        actualizar_luces()

    # Si cambia la aplicación
    if home_sensor != LUCES_CASA[0].value:
        ULTIMO_CAMBIO_LUCES = LightsChanger.API
        actualizar_luces()


def reset_house_state(temp_message_thread, house_state, new_house_state, myhs):
    if temp_message_thread is not None:
        if (
            not temp_message_thread.is_alive()
            and myhs.new_house_state[0] != myhs.house_state[0]
        ):
            myhs.house_state = myhs.new_house_state
            house_state = new_house_state
            lcd_message(myhs.house_state[0], myhs.house_state[1])
    elif temp_message_thread is None and myhs.new_house_state[0] != myhs.house_state[0]:
        myhs.house_state = myhs.new_house_state
        house_state = new_house_state
        lcd_message(myhs.house_state[0], myhs.house_state[1])


def guardar_botones(password):
    # LOGICA CONTRA
    if BOTON_GRUPO.value and BOTON_GRUPO not in password:
        password.append(BOTON_GRUPO)
        print("BOTON GRUPO GUARDADO")
    elif BOTON_SECCION.value and BOTON_SECCION not in password:
        password.append(BOTON_SECCION)
        print("BOTON_SECCION GUARDADO")
    elif BOTON_ASTERISCO.value and BOTON_ASTERISCO not in password:
        password.append(BOTON_ASTERISCO)
        print("BOTON_ASTERISCO GUARDADO")
    return password


def verificar_password(password):
    aceptada = False
    counter = 0
    for item in [BOTON_GRUPO, BOTON_SECCION, BOTON_ASTERISCO]:
        if password[counter] != item:
            aceptada = False
            break
        else:
            aceptada = True
            counter += 1

    if aceptada:
        SMARTHOME.success = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print("PASSWORD CORRECTA")
        return aceptada
    else:
        print("PASSWORD INCORRECTA")
        SMARTHOME.failure = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return aceptada


def bloquear_casa():
    for i in range(15, 0, -1):
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Fallido Espere")
        lcd.move_to(7, 1)
        lcd.putstr(str(i + 1))
        sleep(1)


def lcd_temp_message(state: list, line1="", line2=""):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(line1)
    lcd.move_to(0, 1)
    lcd.putstr(line2)

    sleep(5)

    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(state[0])
    lcd.move_to(0, 1)
    lcd.putstr(state[1])
    sleep(0.5)


def lcd_message(line1="", line2=""):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(line1)
    lcd.move_to(0, 1)
    lcd.putstr(line2)
    sleep(0.5)


def read_adc(channel):
    adc = spi.xfer2([6 | (channel & 4) >> 2, (channel & 3) << 6, 0])
    data = ((adc[1] & 15) << 8) + adc[2]
    return data


class MyHouseState:
    def __init__(self) -> None:

        current_date = datetime.now()
        self.formatted_date = current_date.strftime("%d/%m/%Y")
        self.house_state = ["", self.formatted_date]
        self.new_house_state = ["", self.formatted_date]

    def __str__(self) -> str:
        return f"HS: {self.house_state}, NHS: {self.new_house_state}"


def close_db_connection():
    response = requests.post(API_URL + "close", json=SMARTHOME.to_dict())


if __name__ == "__main__":
    from threading import Thread

    state_thread = Thread(target=handle_state_socket, args=[SMARTHOME])
    command_thread = Thread(target=handle_command_socket, args=[SMARTHOME])
    state_thread.start()
    command_thread.start()
    try:
        main()
    except KeyboardInterrupt:
        close_db_connection()
    finally:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Goodbye!")
        sleep(0.5)
        spi.close()
        state_thread.join()
        command_thread.join()
