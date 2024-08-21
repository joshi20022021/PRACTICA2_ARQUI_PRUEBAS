from lcd_api import LcdApi
from i2c_lcd import I2cLcd

import RPi.GPIO as GPIO
import spidev

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

# Puerto de la temperatura
channel_temp = 0

# Configuraciones
GPIO.setmode(GPIO.BOARD)


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

SENSOR_FUEGO = 32
ROCIADORES = 40
ALARMA = 32

BOTON_RIEGO = 35
REGADORES = 38


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

    GPIO.setup(SENSOR_FUEGO, GPIO.IN)
    GPIO.setup(ROCIADORES, GPIO.OUT)
    GPIO.setup(ALARMA, GPIO.OUT)

    GPIO.setup(BOTON_RIEGO, GPIO.IN)
    GPIO.setup(REGADORES, GPIO.OUT)

    # lista para contraseña
    password = []

    # bandera para saber que el boton enter ya no esta siendo presionado
    enter_reiniciado = False

    # TODO set house state to be dynamic
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d/%m/%Y")
    house_state = ["Temp 27 c", formatted_date]
    new_house_state = house_state

    lcd_message(house_state[0], house_state[1])

    temp_message_thread = None

    # BOTON DE LUZ APAGADO
    while True:
        # LOGICA SENSOR FUEGO
        if GPIO.input(SENSOR_FUEGO) == 1:
            GPIO.output(ROCIADORES, GPIO.HIGH)
            GPIO.output(ALARMA, GPIO.HIGH)
        else:
            GPIO.output(ROCIADORES, GPIO.LOW)
            GPIO.output(ALARMA, GPIO.HIGH)

        # LOGICA DE AIRE ACONDICIONADO
        # print(GPIO.input(TEMP_HUMD_DATA))

        # LOGICA PARA EL BOTON ENTER INICIAL
        if GPIO.input(BOTON_ENTER) == 1 and enter_reiniciado:
            lcd_message(house_state[0], house_state[1])

        # LOGICA CONTRA
        if (
            GPIO.input(BOTON_GRUPO) == 1
            and not BOTON_GRUPO in password
            and enter_reiniciado
        ):
            password.append(BOTON_GRUPO)
            print("BOTON GRUPO GUARDADO")
        elif (
            GPIO.input(BOTON_SECCION) == 1
            and not BOTON_SECCION in password
            and enter_reiniciado
        ):
            password.append(BOTON_SECCION)
            print("BOTON_SECCION GUARDADO")
        elif (
            GPIO.input(BOTON_ASTERISCO) == 1
            and not BOTON_ASTERISCO in password
            and enter_reiniciado
        ):
            password.append(BOTON_ASTERISCO)
            print("BOTON_ASTERISCO GUARDADO")

        # print(password, enter_reiniciado, GPIO.input(BOTON_ENTER))

        if GPIO.input(BOTON_ENTER) == 1 and len(password) == 3 and enter_reiniciado:
            # enviar informacion al display
            counter = 0
            valid = False
            for item in [BOTON_GRUPO, BOTON_SECCION, BOTON_ASTERISCO]:
                if password[counter] != item:
                    valid = False
                    break
                else:
                    valid = True
                    counter += 1

            if valid:
                temp_message_thread = threading.Thread(
                    target=lcd_temp_message, args=(house_state, "Password", "Correcta")
                )
                temp_message_thread.start()
                print("PASSWORD CORRECTA")
            else:
                temp_message_thread = threading.Thread(
                    target=lcd_temp_message,
                    args=(house_state, "Password", "Incorrecta"),
                )
                temp_message_thread.start()
                print("PASSWORD INCORRECTA")

            password = []
            enter_reiniciado = False
        if GPIO.input(BOTON_ENTER) == 0:
            enter_reiniciado = True

        # LOGICA DE TEMPERATURA
        # Leer temperatura
        temp_level = ReadChannel(channel_temp)
        temp = ConvertTemp(temp_level, 2)
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

        # LOGICA LUCES DE LA CASA
        ENCENDIDAS = GPIO.input(ENCENDER_LUCES) == 1
        # LOGICA LUCES DE LA CASA
        print(ENCENDIDAS)
        if GPIO.input(SENSOR_LUZ) == 0:
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

                # LOGICA BOTON DE RIEGO
        if GPIO.input(BOTON_RIEGO) == 1:
            GPIO.output(REGADORES, GPIO.HIGH)
            lcd_temp_message(new_house_state, "Regando", "Invernadero")
        else:
            GPIO.output(REGADORES, GPIO.LOW)

        if temp_message_thread != None:
            if (
                not temp_message_thread.is_alive()
                and new_house_state[0] != house_state[0]
            ):
                house_state = new_house_state

                lcd_message(house_state[0], house_state[1])

        elif temp_message_thread == None and new_house_state[0] != house_state[0]:
            house_state = new_house_state
            lcd_message(house_state[0], house_state[1])

        sleep(0.1)


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
