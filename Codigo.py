from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from states import HouseStates

import RPi.GPIO as GPIO
import spidev
import adafruit_dht
import board


import threading
from datetime import datetime
from time import sleep


# LCD DISPLAY
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

lcd = I2cLcd(1, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.5

# Variables para el sensor de luz
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 100000

LUZ_CHANNEL = 0
GAS_CHANNEL = 1

# Sensor de temp y humedad
DHT11_DEV = adafruit_dht.DHT11(board.D21)


# Configuraciones
# GPIO.setmode(GPIO.BOARD)


# Leer puerto de la temperatura
def ReadChannel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data


# Voltaje recibido a la temperatura
def ConvertTemp(data, places):
    temp = (data * 330) / float(1023)
    temp = round(temp, places)
    return temp


####################
LUCES_CASA = [33]
SENSOR_LUZ = 31

ENCENDER_LUCES = 36

BOTON_AIRE = 11

ALARMA = 32
ROCIADORES = 40

BOTON_RIEGO = 35
REGADORES = 38

TEMP_HUMD = 21


## Contrasena
BOTON_SECCION = 13
BOTON_ASTERISCO = 18
BOTON_GRUPO = 7
BOTON_ENTER = 29


def main():
    # Main program block
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)  # Use BOARD GPIO numbers
    ##################

    GPIO.setup(15, GPIO.OUT)
    GPIO.setup(16, GPIO.OUT)

    # ENCENDER Y APAGAR LUZ CON SENSOR
    for pin in LUCES_CASA:
        GPIO.setup(pin, GPIO.OUT)

    GPIO.setup(SENSOR_LUZ, GPIO.IN)
    GPIO.setup(ENCENDER_LUCES, GPIO.IN)

    GPIO.setup(BOTON_GRUPO, GPIO.IN)  # primero
    GPIO.setup(BOTON_SECCION, GPIO.IN)  # segundo
    GPIO.setup(BOTON_ASTERISCO, GPIO.IN)  # tercero
    GPIO.setup(BOTON_ENTER, GPIO.IN)

    GPIO.setup(BOTON_AIRE, GPIO.IN)

    # GPIO.setup(SENSOR_FUEGO, GPIO.IN)
    GPIO.setup(ROCIADORES, GPIO.OUT)
    GPIO.setup(ALARMA, GPIO.OUT)

    GPIO.setup(BOTON_RIEGO, GPIO.IN)
    GPIO.setup(REGADORES, GPIO.OUT)

    # lista para contraseña
    password = []

    # TODO set house state to be dynamic
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d/%m/%Y")
    house_state = ["Temp 27 c", formatted_date]
    new_house_state = house_state

    lcd_message(house_state[0], house_state[1])

    temp_message_thread = None
    blocked_thread = None

    intento = 0

    estado_actual_casa = HouseStates.NORMAL

    # BOTON DE LUZ APAGADO
    while True:
        # When is in normal mode
        if estado_actual_casa == HouseStates.NORMAL:
            new_house_state = sensor_temperatura(formatted_date)
            luces_casa()
            sensor_fuego()
            reset_house_state(temp_message_thread, house_state, new_house_state)

            if GPIO.input(BOTON_ENTER) == 1:
                estado_actual_casa = HouseStates.PASSWORD
                lcd_message("Ingrese Password", "***")

        # When is in Blocked node
        elif estado_actual_casa == HouseStates.BLOCKED:
            # print("ESTAMOS BLOQUANDO LA CASA")
            new_house_state = sensor_temperatura(formatted_date)
            sensor_fuego()
            luces_casa()
            if blocked_thread != None:
                if not blocked_thread.is_alive():
                    estado_actual_casa = HouseStates.NORMAL
                    blocked_thread = None
                    sleep(0.5)
            else:
                blocked_thread = threading.Thread(target=bloquear_casa)
                blocked_thread.start()

        # When is in Password mode
        elif estado_actual_casa == HouseStates.PASSWORD:
            new_house_state = sensor_temperatura(formatted_date)
            sensor_fuego()
            luces_casa()
            if len(password) < 3:
                password = guardar_botones(password)
            elif len(password) == 3 and GPIO.input(BOTON_ENTER) == 1:
                aceptado = verificar_password(password, house_state)
                password = []

                if aceptado:
                    intento = 0

                    temp_message_thread = threading.Thread(
                        target=lcd_temp_message,
                        args=(new_house_state, "Password", "Correcta"),
                    )
                    temp_message_thread.start()
                    estado_actual_casa = HouseStates.NORMAL

                if not aceptado:
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
    gas_value = read_adc(GAS_CHANNEL)  # Leer canal 0 (foto resistencia)
    if gas_value > 1500:
        GPIO.output(ROCIADORES, GPIO.HIGH)
        GPIO.output(ALARMA, GPIO.HIGH)
    else:
        GPIO.output(ROCIADORES, GPIO.LOW)
        GPIO.output(ALARMA, GPIO.LOW)


def sensor_temperatura(formatted_date):
    # LOGICA DE TEMPERATURA
    # Leer temperatura
    # temp_level = ReadChannel(channel_temp)
    # temp = ConvertTemp(temp_level, 2)

    temperature = DHT11_DEV.temperature
    humidity = DHT11_DEV.humidity

    # Reading the DHT11 is very sensitive to timings and occasionally
    # the Pi might fail to get a valid reading. So check if readings are valid.
    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
    else:
        print("Failed to get reading. Try again!")

    temp = 0
    new_house_state = ["Temp " + str(int(temp)) + " c", formatted_date]
    if temp > 27 and GPIO.input(BOTON_AIRE) == 0:
        GPIO.output(15, GPIO.HIGH)
        GPIO.output(16, GPIO.LOW)
        sleep(0.5)
        GPIO.output(15, GPIO.LOW)
        GPIO.output(16, GPIO.HIGH)
    elif temp > 27 and GPIO.input(BOTON_AIRE) == 1:
        GPIO.output(15, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)
    else:
        GPIO.output(15, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)

    return new_house_state


def luces_casa():
    # LOGICA LUCES DE LA CASA
    ENCENDIDAS = GPIO.input(ENCENDER_LUCES) == 1
    light_value = read_adc(LUZ_CHANNEL)  # Leer canal 0 (foto resistencia)
    # LOGICA LUCES DE LA CASA
    if light_value > 500:
        # print("Canal 0: ", light_value)
        if ENCENDIDAS:
            for pin in LUCES_CASA:
                GPIO.output(pin, GPIO.HIGH)
        else:
            for pin in LUCES_CASA:
                GPIO.output(pin, GPIO.LOW)
    else:
        if ENCENDIDAS:
            for pin in LUCES_CASA:
                GPIO.output(pin, GPIO.LOW)
        else:
            for pin in LUCES_CASA:
                GPIO.output(pin, GPIO.HIGH)


def reset_house_state(temp_message_thread, house_state, new_house_state):
    if temp_message_thread != None:
        if not temp_message_thread.is_alive() and new_house_state[0] != house_state[0]:
            house_state = new_house_state

            lcd_message(house_state[0], house_state[1])

    elif temp_message_thread == None and new_house_state[0] != house_state[0]:
        house_state = new_house_state
        lcd_message(house_state[0], house_state[1])


def guardar_botones(password):
    # LOGICA CONTRA
    if GPIO.input(BOTON_GRUPO) == 1 and not BOTON_GRUPO in password:
        password.append(BOTON_GRUPO)
        print("BOTON GRUPO GUARDADO")
    elif GPIO.input(BOTON_SECCION) == 1 and not BOTON_SECCION in password:
        password.append(BOTON_SECCION)
        print("BOTON_SECCION GUARDADO")
    elif GPIO.input(BOTON_ASTERISCO) == 1 and not BOTON_ASTERISCO in password:
        password.append(BOTON_ASTERISCO)
        print("BOTON_ASTERISCO GUARDADO")
    return password


def verificar_password(password, house_state):
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
    sleep(E_DELAY)


def lcd_message(line1="", line2=""):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(line1)
    lcd.move_to(0, 1)
    lcd.putstr(line2)
    sleep(E_DELAY)


def read_adc(channel):
    adc = spi.xfer2([6 | (channel & 4) >> 2, (channel & 3) << 6, 0])
    data = ((adc[1] & 15) << 8) + adc[2]
    return data


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Goodbye!")
        sleep(E_DELAY)
        spi.close()
