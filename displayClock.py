#!/usr/bin/python3 -u

import socket
import time
import array
import datetime
import requests

sseg = {
        0: [ 0xFE, 0x82, 0x82, 0xFE ],
        1: [ 0x00, 0x00, 0x00, 0xFE ],
        1: [ 0xFE ],
        2: [ 0xF2, 0x92, 0x92, 0x9E ],
        3: [ 0x82, 0x92, 0x92, 0xFE ],
        4: [ 0x1E, 0x10, 0x10, 0xFE ],
        5: [ 0x9E, 0x92, 0x92, 0xF2 ],
        6: [ 0xFE, 0x90, 0x90, 0xF0 ],
        7: [ 0x02, 0x02, 0x02, 0xFE ],
        8: [ 0xFE, 0x92, 0x92, 0xFE ],
        9: [ 0x1E, 0x12, 0x12, 0xFE ],
        ':': [ 0x28 ],
        ' ': [ 0x00 ],
    }

zseg = dict(sseg)
zseg[0] = [ 0, 0, 0, 0 ]

UDP_IP = "esp-dotmatrix.local"
UDP_PORT = 1234

def get_temp():
    try:
        r = requests.get("https://tmep.cz/vystup-json.php?id=5525&export_key=1zpjfwd7yk", timeout=1)
        return int(r.json()["teplota"])
    except Exception as e:
        print(e)
        return 99
    return 98

def get_temp_influx():
    try:
        query = """SELECT last(value) FROM "°C" WHERE (entity_id = 'outside_temperature')"""
        r = requests.get("http://10.7.0.1:8086/query?db=home_assistant&q=" + requests.utils.quote(query), timeout=1)
        return int(r.json()["results"][0]["series"][0]["values"][0][1])
    except Exception as e:
        print(e)
        return 99
    return 98

def format_number(number):
    ret = []

    if number < 0:
        ret += [4]
    else:
        sign = 0
    anumber = abs(number)
    tens = anumber//10
    ones = anumber%10

    if tens > 0:
        ret += sseg[tens]
        ret += sseg[' ']

    ret += sseg[ones]

    return ret

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
oldnow = time.localtime(time.time())
temp = get_temp()
while True:
    now = time.localtime(time.time())
    if oldnow.tm_sec % 10 == 0:
        temp = get_temp()
    if now.tm_sec != oldnow.tm_sec:

        data = [ 2 ]
        if now.tm_sec == 0:
            data[0] += 0x80
        data += format_number(now.tm_hour)
        data += sseg[' ']
        data += sseg[':']
        data += sseg[' ']
        data += format_number(now.tm_min)
        data += sseg[' ']
        data.append(pow(2, now.tm_sec*8//60) - 1)
#            [now.tm_sec]
        data += sseg[' ']
        data += format_number(now.tm_mday)
        data += sseg[' ']
        data += [128]
        data += sseg[' ']
        data += format_number(now.tm_mon)
        data += sseg[' ']
        data += [128]
        data += sseg[' ']

# temp
        data += format_number(temp)
        #print(data)
        sock.sendto(bytes(data), (UDP_IP, UDP_PORT))
    oldnow = now
    time.sleep(0.1)
