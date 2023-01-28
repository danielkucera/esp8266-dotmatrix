#!/usr/bin/python3 -u

import socket
import time
import array
import datetime
import requests

sseg = {
        0: [ 0xFE, 0x82, 0x82, 0xFE ],
        1: [ 0x00, 0x00, 0x00, 0xFE ],
        2: [ 0xF2, 0x92, 0x92, 0x9E ],
        3: [ 0x92, 0x92, 0x92, 0xFE ],
        3: [ 0x92, 0x92, 0x92, 0xFE ],
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

def format_temp(temp):
    if temp < 0:
        sign = 4
    else:
        sign = 0
    tens = abs(temp)//10
    ones = abs(temp)%10

    return [sign] + zseg[tens] + sseg[ones]

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
oldnow = time.localtime(time.time())
temp = get_temp()
while True:
    now = time.localtime(time.time())
    if oldnow.tm_sec % 10 == 0:
        temp = get_temp()
    if now.tm_sec != oldnow.tm_sec:

        data = []
        data += zseg[now.tm_hour//10]
        data += sseg[' ']
        data += sseg[now.tm_hour%10]
        data += sseg[' ']
        data += sseg[':']
        data += sseg[' ']
        data += sseg[now.tm_min//10]
        data += sseg[' ']
        data += sseg[now.tm_min%10]
        data += sseg[' ']
        data.append(pow(2, now.tm_sec*8//60) - 1)
#            [now.tm_sec]
        data += format_temp(temp)
        #print(data)
        sock.sendto(bytes(data), (UDP_IP, UDP_PORT))
    oldnow = now
    time.sleep(0.1)
