##################################################
#                                                #
# Software controller for led display LTC5854AHG #
#                                                #
##################################################

#####################
# GPIO Connection
#
# pins 1 -> 14 (skipping the missing ones) should be connected to lcd gpios in a diagonal alternate fashion:
# 1  -> LCD-D3
# 2  -> LCD-D6
# 3  -> LCD-D7
# 4  -> LCD-D12
# 6  -> LCD-D13
# 7  -> LCD-D18
# 8  -> LCD-D19
# 9  -> LCD-D22
# 11 -> LCD-D23
# 12 -> LCD-VSYNC
# 14 -> LCD-DE
#
# pins 16 -> 25 (skipping anode pins) should be connected to XIO pins in order:
# 16 -> XIO-P0
# 17 -> XIO-P1
# 19 -> XIO-P2
# 20 -> XIO-P3
# 21 -> XIO-P4
# 22 -> XIO-P5
# 24 -> XIO-P6
# 25 -> XIO-P7
#
# pins 26 -> 30 (skipping anode pin) should be connected to CSI pins in order:
# 26 -> CSID0
# 27 -> CSID1
# 29 -> CSID2
# 30 -> CSID3
#
# anode pins should be connected to 3v3 power:
# 18 -> 3V3
# 23 -> 3V3
# 28 -> 3V3
#
#####################

import CHIP_IO.GPIO as gpio
import CHIP_IO.Utilities
import time

pin_map = {
    1  : "LCD-D3",
    2  : "LCD-D6",
    3  : "LCD-D7",
    4  : "LCD-D12",
    6  : "LCD-D13",
    7  : "LCD-D18",
    8  : "LCD-D19",
    9  : "LCD-D22",
    11 : "LCD-D23",
    12 : "LCD-VSYNC",
    14 : "LCD-DE",
    16 : "XIO-P0",
    17 : "XIO-P1",
    19 : "XIO-P2",
    20 : "XIO-P3",
    21 : "XIO-P4",
    22 : "XIO-P5",
    24 : "XIO-P6",
    25 : "XIO-P7",
    26 : "CSID0",
    27 : "CSID1",
    29 : "CSID2",
    30 : "CSID3"
}

digit_maps = [
        {
            0: 27,
            1: 26,
            2: 4,
            3: 2,
            4: 1,
            5: 29,
            6: 30
            },
        {
            0: 22,
            1: 21,
            2: 9,
            3: 7,
            4: 6,
            5: 24,
            6: 25
            },
        {
            0: 17,
            1: 16,
            2: 14,
            3: 12,
            4: 11,
            5: 19,
            6: 20
            }
]

all_leds = [x for x in pin_map.keys()]

full_digits = []
for d in digit_maps:
    full_digits.append([x for x in d.values()])

for i in pin_map.values():
    gpio.cleanup(i)
CHIP_IO.Utilities.unexport_all()
for i in pin_map.values():
    gpio.setup(i, gpio.OUT)
    gpio.output(i, gpio.HIGH)

def turnon(n):
    global pin_map
    if type(n) is list:
        for l in n:
            gpio.output(pin_map[l], gpio.LOW)
    else:
        turnon([n])

def turnoff(n):
    global pin_map
    if type(n) is list:
        for l in n:
            gpio.output(pin_map[l], gpio.HIGH)
    else:
        turnoff([n])

font = {
        "a" : [4, 5, 0, 1, 2, 6],
        "b" : [2, 3, 4, 5, 6],
        "c" : [0, 3, 4, 5],
        "d" : [1, 2, 3, 4, 6],
        "e" : [0, 3, 4, 5, 6],
        "f" : [0, 4, 5, 6],
        "g" : [0, 2, 3, 4, 5],
        "h" : [2, 4, 5, 6],
        "i" : [4],
        "j" : [1, 2, 3],
        "k" : [1, 2, 4, 5, 6],
        "l" : [3, 4, 5],
        "m" : [0, 1, 2, 4, 5],
        "n" : [2, 4, 6],
        "o" : [2, 3, 4, 6],
        "p" : [0, 1, 4, 5, 6],
        "q" : [0, 1, 2, 5, 6],
        "r" : [4, 6],
        "s" : [0, 2, 3, 5, 6],
        "t" : [0, 4, 5],
        "u" : [2, 3, 4],
        "v" : [1, 2, 3, 4, 5],
        "x" : [1, 2, 4, 5, 6],
        "y" : [1, 2, 5, 6],
        "z" : [0, 1, 3, 4, 6],
        "0" : [0, 1, 2, 3, 4, 5],
        "1" : [4, 5],
        "2" : [0, 1, 3, 4, 6],
        "3" : [0, 1, 2, 3, 6],
        "4" : [1, 4, 5, 6],
        "5" : [0, 2, 3, 5, 6],
        "6" : [0, 2, 3, 4, 5, 6],
        "7" : [0, 1, 2],
        "8" : [0, 1, 2, 3, 4, 5, 6],
        "9" : [0, 1, 2, 3, 5, 6],
        "." : [3],
        ":" : [3, 8]
        }

def get_char(c, pos):
    global font
    global digit_maps

    if pos >= len(digit_maps):
        return None

    if c not in ".:":
        return [digit_maps[pos][x] for x in font[c.lower()]]
    else:
        return font[c]

def write_char(c, pos):
    global full_digits
    
    if pos >= len(full_digits):
        return -1
    turnoff(full_digits[pos])

    if c is not None and c != " ":
        turnon(get_char(c, pos))
    return 0

def write_str(s, duration):
    letter_duration = float(duration) / len(s)

    d0 = None
    d1 = None
    d2 = None
    s += "  "

    for c in s:
        d0 = d1
        d1 = d2
        d2 = c
        write_char(d0, 0)
        write_char(d1, 1)
        write_char(d2, 2)
        time.sleep(letter_duration)
    
    write_char(None, 0)

