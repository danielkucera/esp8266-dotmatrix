#!/usr/bin/python

import socket
import time
import array
import datetime

sseg = {
        '0': [ 0xFE, 0x82, 0x82, 0xFE ],
        '1': [ 0x00, 0x00, 0x00, 0xFE ],
        '2': [ 0xF2, 0x92, 0x92, 0x9E ],
        '3': [ 0x92, 0x92, 0x92, 0xFE ],
        '4': [ 0x1E, 0x10, 0x10, 0xFE ],
        '5': [ 0x9E, 0x92, 0x92, 0xF2 ],
        '6': [ 0xFE, 0x90, 0x90, 0xF0 ],
        '7': [ 0x02, 0x02, 0x02, 0xFE ],
        '8': [ 0xFE, 0x92, 0x92, 0xFE ],
        '9': [ 0x1E, 0x12, 0x12, 0xFE ],
        ':': [ 0x28 ],
    }

UDP_IP = "esp-dotmatrix.local"
UDP_PORT = 1234

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

while True:
    now = time.localtime(time.time())

    data = array.array('B', 
            sseg[str(now.tm_hour/10)] + [0] +
            sseg[str(now.tm_hour%10)] + [0] +
            sseg[':'] + [0] +
            sseg[str(now.tm_min/10)] + [0] +
            sseg[str(now.tm_min%10)] + [0] +
            [2**(7-now.tm_sec*8/60)] + [0] +
            [now.tm_sec]
            ).tostring()

    sock.sendto(data, (UDP_IP, UDP_PORT))
    time.sleep(0.3)
