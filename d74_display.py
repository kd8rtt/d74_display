#!/usr/bin/python
# Example using a character LCD connected to a Raspberry Pi
import time
import Adafruit_CharLCD as LCD
import serial
import os
import csv

# Functions definition
def switch_mode(argument):
    switcher = {
        0: "FM",
        1: "DV",
        2: "AM",
        3: "LSB",
        4: "USB",
        5: "CW",
        6: "NFM",
        7: "DR",
        8: "WFM",
        9: "R-CW"
    }
    return switcher.get(argument, "INV")

# this function loads in the memory file
#  and checks the receieved memory channel
#  number against the list of names
def mem_name(ch_num):
    fieldnames = [
        '!!Ch',
        'Rx Freq.',
        'Rx Step',
        'Offset',
        'T/CT/DCS',
        'TO Freq.',
        'CT Freq.',
        'DCS Code',
        'Shift/Split',
        'Rev.',
        'L.Out',
        'Mode',
        'Tx Freq.',
        'Tx Step',
        'M.Name'
    ]

    try:
        with open('/home/pi/d74_display/d74_memory.hmk', 'r') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames = fieldnames)
            for row in reader:
                if ch_num in row['!!Ch']:
                    mem_txt = row['M.Name']
                    return mem_txt
                else:
                    mem_txt = 'None'
            if mem_txt == 'None':
                return mem_txt
    # if no memory file is found, treat it like an unnammed memory channel
    except:
        mem_txt = 'None'
        return mem_txt

# Raspberry Pi pin setup
lcd_rs = 25
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 18
lcd_d7 = 22
lcd_backlight = 2

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4,
                           lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)

# Try to connect to the D74 and run the program
try:
    ser = serial.Serial('/dev/ttyACM0', baudrate=9600,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        bytesize=serial.EIGHTBITS,
                                        timeout = 0.5)
    ser.flushInput()
    ser.flushOutput()
    ser.write('BL\r'.encode()) # get battery capacity to confirm proper operation
    init_data = ser.read(4)
    if init_data[3] == "0":
        p_f = "TH-D74 OK\nBattery: <25%"
    elif init_data[3] == "1":
        p_f = "TH-D74 OK\nBattery: >25%"
    elif init_data[3] == "2":
        p_f = "TH-D74 OK\nBattery: >50%"
    elif init_data[3] == "3":
        p_f = "TH-D74 OK\nBattery: >75%"
    elif init_data[3] == "4":
        p_f = "TH-D74 OK\nCharging"
    else:
        raise Exception("TH-D74 FAIL")
    lcd.message(p_f)
    ser.flushInput()
    time.sleep(3)
    lcd.clear()
    while(1):
        ser.write('BC\r'.encode()) # sets selected band (0 = band a, 1 = band b)
        bnd_data = ser.read(4)
        a_b = bnd_data[3]
        ser.flushInput()
    ser.flushOutput()
    get_mem = 'MR ' + a_b + '\r'
    ser.write(get_mem.encode()) # get memory channel mode and channel
    mem_data = ser.read(6)
    if mem_data[0] == 'N':
        print 'no mem'
        mem_txt = 'None'
    else:
        input_num = '0' + mem_data[3:6]
        mem_txt = mem_name(input_num)
        print mem_txt
        ser.flushInput()
        freq_active = 'FO ' + a_b + '\r'
        ser.write(freq_active.encode()) # get current frequency and mode
        f_data = ser.read(50)
        mhz_string = f_data[6:9]
        khz_string = f_data[9:12]
        hz_string = f_data[12:14]
        freq_string = mhz_string + "." + khz_string + "." + hz_string + " MHz"
        mode_raw = f_data[31]
        mode = switch_mode(int(mode_raw))
        ser.flushInput()
        ser.write('RT\r'.encode()) # get current time and date
        d_time = ser.read(15)
        utc = d_time[5:7] + "/" + d_time[7:9] + "  " + d_time[9:11] + ":" + d_time[11:13] + ":" + d_time[13:15] + "Z"
        if mem_txt == 'None': # if no memory channel name, just display frequency, mode, and date/time
             lcd_out = freq_string + " " + mode[0] + "\n" + utc
        else:
             spaces = 16 - len(mem_txt)
             for i in range(spaces):
                 mem_txt = mem_txt + ' '
             lcd_out = mem_txt + '\n' + utc # if there is a memory channel, display it and date/time
    lcd.message(lcd_out)
    lcd.home()
    time.sleep(0.1) # polls the D74 ten times per second for changes
    ser.flushInput()
    ser.flushOutput()
    print lcd_out
# if an error is encountered at any point,
#  print a message to the LCD and shutdown the Pi
except:
    lcd.clear()
    p_f = "TH-D74 FAIL"
    lcd.message(p_f)
    time.sleep(5)
    ser.close()
    lcd.clear()
    os.system('sudo poweroff')
finally:
    lcd.clear()
    pass