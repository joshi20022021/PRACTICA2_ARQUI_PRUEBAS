import RPi.GPIO as GPIO
import threading
from datetime import datetime
from time import sleep
import spidev

# Definir los pines
LDR_PIN = 29
LED_PIN = 31

# Define GPIO to LCD mapping (using BOARD numbering)
LCD_RS = 26  # BOARD pin 37
LCD_E = 12  # BOARD pin 18
LCD_D4 = 13  # BOARD pin 15
LCD_D5 = 37  # BOARD pin 12
LCD_D6 = 22  # BOARD pin 36
LCD_D7 = 18 # BOARD pin 32

# Define some device constants
LCD_WIDTH = 16  # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

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
    temp = ((data * 330) / float(1023))
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
BOTON_SECCION = 3
BOTON_ASTERISCO = 5
BOTON_GRUPO = 7
BOTON_ENTER = 29




def main():
    # Main program block
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)  # Use BOARD GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_RS, GPIO.OUT)  # RS
    GPIO.setup(LCD_D4, GPIO.OUT)  # DB4
    GPIO.setup(LCD_D5, GPIO.OUT)  # DB5
    GPIO.setup(LCD_D6, GPIO.OUT)  # DB6
    GPIO.setup(LCD_D7, GPIO.OUT)  # DB7
    GPIO.setup(LDR_PIN, GPIO.IN)
    GPIO.setup(LED_PIN, GPIO.OUT)
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

    # Initialise display
    lcd_init()

    # lista para contraseña
    password = []

    # bandera para saber que el boton enter ya no esta siendo presionado
    enter_reiniciado = False

    # TODO set house state to be dynamic
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d/%m/%Y")
    house_state = ["Temp 27 c", formatted_date]
    new_house_state = house_state

    lcd_string(house_state[0], LCD_LINE_1)
    lcd_string(house_state[1], LCD_LINE_2)

    message_thread = None

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
        #print(GPIO.input(TEMP_HUMD_DATA))

        # LOGICA PARA EL BOTON ENTER INICIAL
        if GPIO.input(BOTON_ENTER) == 1 and enter_reiniciado:
            lcd_string("Ingresar Patron", LCD_LINE_1)
            lcd_string("***", LCD_LINE_2)

        # LOGICA CONTRA
        if GPIO.input(BOTON_GRUPO) == 1 and not BOTON_GRUPO in password and enter_reiniciado:
            password.append(BOTON_GRUPO)
            print("BOTON GRUPO GUARDADO")
        elif GPIO.input(BOTON_SECCION) == 1 and not BOTON_SECCION in password and enter_reiniciado:
            password.append(BOTON_SECCION)
            print("BOTON_SECCION GUARDADO")
        elif GPIO.input(BOTON_ASTERISCO) == 1 and not BOTON_ASTERISCO in password and enter_reiniciado:
            password.append(BOTON_ASTERISCO)
            print("BOTON_ASTERISCO GUARDADO")

        #print(password, enter_reiniciado, GPIO.input(BOTON_ENTER))

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
                message_thread = threading.Thread(target=lcd_temp_message, args=(house_state, "Password", "Correcta"))
                message_thread.start()
                print("PASSWORD CORRECTA")
            else:
                message_thread = threading.Thread(target=lcd_temp_message, args=(house_state, "Password", "Incorrecta"))
                message_thread.start()
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

        if message_thread != None:
            if not message_thread.is_alive() and new_house_state[0] != house_state[0]:
                house_state = new_house_state
                lcd_byte(0x01, LCD_CMD)
                sleep(E_DELAY)
                lcd_string(house_state[0], LCD_LINE_1)
                lcd_string(house_state[1], LCD_LINE_2)

        elif message_thread == None and new_house_state[0] != house_state[0]:
                house_state = new_house_state
                lcd_byte(0x01, LCD_CMD)
                sleep(E_DELAY)
                lcd_string(house_state[0], LCD_LINE_1)
                lcd_string(house_state[1], LCD_LINE_2)


        sleep(0.1)


def lcd_temp_message(state: list, line1="", line2=""):
    lcd_string(line1, LCD_LINE_1)
    lcd_string(line2, LCD_LINE_2)

    sleep(5)

    lcd_string(state[0], LCD_LINE_1)
    lcd_string(state[1], LCD_LINE_2)


def lcd_init():
    # Initialise display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On, Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    sleep(E_DELAY)


def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True  for character
    #        False for command

    GPIO.output(LCD_RS, mode)  # RS

    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40: GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()


def lcd_toggle_enable():
    # Toggle enable
    sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    sleep(E_DELAY)


def lcd_string(message, line):
    # Send string to display

    message = message.ljust(LCD_WIDTH, " ")

    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)


if __name__ == "main":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcd_byte(0x01, LCD_CMD)
        lcd_string("Goodbye!", LCD_LINE_1)
