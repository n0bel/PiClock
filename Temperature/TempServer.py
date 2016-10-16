#!/usr/bin/python
# small web server that polls 18B20's that it finds
# and makes them available as a json response
# see TempNames.py for sensor id to name mapping
#
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from w1thermsensor import W1ThermSensor
import json
import time
import socket
from threading import Thread, Lock
from TempNames import sensornames

temps = {}
temptimes = {}
lock = Lock()

PORT_NUMBER = 48213

# This class will handles any incoming request from
# the browser


class myHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers',
                         "x-requested-with, origin, x-csrftoken," +
                         " content-type, accept"
                         )
        self.end_headers()

    def do_GET(self):
        global temps, lock
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        s = {'temp': '', 'temps': {}}
        lock.acquire()
        for k in temps:
            if s['temp'] == '':
                s['temp'] = "%.1f" % temps[k]
            s['temps'][sensorname(k)] = "%.1f" % temps[k]
        lock.release()
        self.wfile.write(json.dumps(s))


def sensorname(str):
    try:
        return sensornames[str]
    except KeyError:
        return 'temp-' + str


def t_http():
    try:
        server = HTTPServer(('0.0.0.0', PORT_NUMBER), myHandler)
        print 'Started httpserver on port ', PORT_NUMBER
        server.serve_forever()
    except:
        server.close()


def t_udp():
    global temps, lock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('', 53535)
    sock.bind(server_address)
    while True:
        data, address = sock.recvfrom(4096)
        (addr, temp) = data.split(':')
        saddr = [addr[i:i + 2] for i in range(0, len(addr), 2)]
        saddr.reverse()
        saddr = saddr[1:7]
        addr = ''.join(saddr)
        tempf = float(temp) * 9.0 / 5.0 + 32.0
        lock.acquire()
        temps[addr] = tempf
        temptimes[addr] = time.time()
        lock.release()
        print 'udp>' + addr + ':' + str(tempf)


def t_temp():
    while True:
        for sensor in W1ThermSensor.get_available_sensors():
            lock.acquire()
            temps[sensor.id] = sensor.get_temperature(W1ThermSensor.DEGREES_F)
            temptimes[sensor.id] = time.time()
            print 'hwr>' + sensor.id + ':' + str(temps[sensor.id])
            lock.release()

        lock.acquire()
        todelete = []
        expire = time.time() - 60 * 10
        for t in temptimes:
            if temptimes[t] < expire:
                todelete.append(t)
        for t in todelete:
            temptimes.pop(t, None)
            temps.pop(t, None)
            print "del>" + t
        lock.release()

        time.sleep(120)

t_httpt = Thread(target=t_http)
t_httpt.daemon = True
t_httpt.start()

t_udpt = Thread(target=t_udp)
t_udpt.daemon = True
t_udpt.start()

t_tempt = Thread(target=t_temp)
t_tempt.daemon = True
t_tempt.start()

try:
    while True:
        time.sleep(.1)
except KeyboardInterrupt:
    exit()
