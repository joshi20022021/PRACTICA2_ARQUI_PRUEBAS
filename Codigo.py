from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from states import HouseStates

import spidev
import adafruit_dht
import board
import digitalio

import threading
from datetime import datetime
from time import sleep

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
GAS_CHANNEL = 1

# Sensor de temp y humedad
DHT11_DEV = adafruit_dht.DHT11(board.D21)

# Configuraciones de pines usando digitalio
LUCES_CASA = [digitalio.DigitalInOut(board.D13)]
SENSOR_LUZ = digitalio.DigitalInOut(board.D6)
ENCENDER_LUCES = digitalio.DigitalInOut(board.D16)
BOTON_AIRE = digitalio.DigitalInOut(board.D17)
ALARMA = digitalio.DigitalInOut(board.D12)
ROCIADORES = digitalio.DigitalInOut(board.D21)
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


def main():
    # Main program block
    ##################
    # ENCENDER Y APAGAR LUZ CON SENSOR
    password = []

    my_state = MyHouseState()
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d/%m/%Y")
    house_state = ["Temp 27 c", formatted_date]
    new_house_state = house_state.copy()

    lcd_message(house_state[0], house_state[1])

    temp_message_thread = None
    blocked_thread = None
    temperature_message_thread = None

    intento = 0
    estado_actual_casa = HouseStates.NORMAL

    # BOTON DE LUZ APAGADO
    while True:
        # When is in normal mode

        if estado_actual_casa == HouseStates.NORMAL:
            # new_house_state = sensor_temperatura(formatted_date)

            if temperature_message_thread != None:
                if not temperature_message_thread.is_alive():
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

            luces_casa()
            sensor_fuego()
            reset_house_state(
                temp_message_thread, house_state, new_house_state, my_state
            )

            if BOTON_ENTER.value:
                estado_actual_casa = HouseStates.PASSWORD
                lcd_message("Ingrese Password", "***")

        # When is in Blocked mode
        elif estado_actual_casa == HouseStates.BLOCKED:
            sensor_fuego()
            luces_casa()
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
            sensor_fuego()
            luces_casa()
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


def sensor_fuego():
    # LOGICA SENSOR FUEGO
    gas_value = read_adc(GAS_CHANNEL)  # Leer canal 1 (sensor de gas)
    # print("VALOR GAS: ", gas_value)
    if gas_value > 1800:
        ROCIADORES.value = True
        ALARMA.value = True
    else:
        ROCIADORES.value = False
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

    new_house_state = ["Temp " + str(temperature) + " C", formatted_date]
    myhs.new_house_state = new_house_state
    sleep(2)
    # return new_house_state


def luces_casa():
    # LOGICA LUCES DE LA CASA
    ENCENDIDAS = ENCENDER_LUCES.value
    light_value = read_adc(LUZ_CHANNEL)  # Leer canal 0 (foto resistencia)
    # print("LUZ CASA: ", light_value)

    if light_value > 500:
        if ENCENDIDAS:
            for pin in LUCES_CASA:
                pin.value = False
        else:
            for pin in LUCES_CASA:
                pin.value = True
    else:
        if ENCENDIDAS:
            for pin in LUCES_CASA:
                pin.value = True
        else:
            for pin in LUCES_CASA:
                pin.value = False


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
        print("PASSWORD CORRECTA")
        return aceptada
    else:
        print("PASSWORD INCORRECTA")
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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Goodbye!")
        sleep(0.5)
        spi.close()
