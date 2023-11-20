#!/usr/bin/env python3
# This file was extracted from an archive provided on http://wiki.sunfounder.cc/index.php?title=I2C_LCD2004
# No license was specified in the original file.

# Modifications were made to make it compatible with command-line arguments for specifying
# lines of text to print to the display if run directly.

import time
import smbus2 as smbus
import sys

BUS = smbus.SMBus(1)

def write_word(addr, data):
    global BLEN
    temp = data
    if BLEN == 1:
        temp |= 0x08
    else:
        temp &= 0xF7
    BUS.write_byte(addr, temp)

def send_command(comm):
    buf = comm & 0xF0
    buf |= 0x04
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB
    write_word(LCD_ADDR, buf)

    buf = (comm & 0x0F) << 4
    buf |= 0x04
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB
    write_word(LCD_ADDR, buf)

def send_data(data):
    buf = data & 0xF0
    buf |= 0x05
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB
    write_word(LCD_ADDR, buf)

    buf = (data & 0x0F) << 4
    buf |= 0x05
    write_word(LCD_ADDR, buf)
    time.sleep(0.002)
    buf &= 0xFB
    write_word(LCD_ADDR, buf)

def init(addr, bl):
    global LCD_ADDR
    global BLEN
    LCD_ADDR = addr
    BLEN = bl
    try:
        send_command(0x33)
        time.sleep(0.005)
        send_command(0x32)
        time.sleep(0.005)
        send_command(0x28)
        time.sleep(0.005)
        send_command(0x0C)
        time.sleep(0.005)
        send_command(0x01)
        BUS.write_byte(LCD_ADDR, 0x08)
    except:
        return False
    else:
        return True

def clear():
    send_command(0x01)

def openlight():
    BUS.write_byte(0x27, 0x08)
    BUS.close()

def write(x, y, str):
    if x < 0:
        x = 0
    if x > 19:
        x = 19
    if y < 0:
        y = 0
    if y > 3:
        y = 3

    # Fixed row addresses
    row_offsets = [0x00, 0x40, 0x14, 0x54]
    addr = 0x80 + row_offsets[y] + x
    send_command(addr)

    for chr in str:
        send_data(ord(chr))

if __name__ == '__main__':
    init(0x3f, 1)
    write(0, 0, sys.argv[1])
    write(0, 1, sys.argv[2])
    write(0, 2, sys.argv[3])
    write(0, 3, sys.argv[4])
