#!/usr/bin/env python3


from time import sleep

from lcd_api import LcdApi
from i2c_lcd import I2cLcd

I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

lcd = I2cLcd(1, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)


while True:
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Sucio el que")
    lcd.move_to(0, 1)
    lcd.putstr("lo lea")

    sleep(0.5)

    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Puerco el que")
    lcd.move_to(0, 1)
    lcd.putstr("lo piense")
    sleep(0.5)
