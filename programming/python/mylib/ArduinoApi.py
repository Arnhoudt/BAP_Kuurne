from multiprocessing import Process

import serial.tools.list_ports
import time
class ArduinoApi:
    arduino = None

    def __init__(self):
        self.connectArduino()


    def tick(self):
        bytesToRead = self.arduino.inWaiting()
        result = self.arduino.read(bytesToRead)
        print(result)

    def connectArduino(self):
        for port in list(serial.tools.list_ports.comports()):
            if port[2].startswith('USB VID:PID=1A86:7523'):
                print("Arduino found on port: " + port[0])
                self.arduino = serial.Serial(port=port[0], baudrate=115200, timeout=1)

    def servo(self, num):
        self.arduino.write(bytes("o"+str(num), 'utf-8'))


    def write(self, value, target):
        if target == "servo":
            self.servo(value)
            return "OK"
        else:
            return "The target does not exist"

    def read(self):
        bytesToRead = self.arduino.inWaiting()
        return self.arduino.read(bytesToRead).decode('utf-8'), 200


    def api(self, method, value = None, target = None):
        if not self.arduino or not self.arduino.is_open:
            self.connectArduino()
            if not self.arduino:
                return "No arduino has been found", 404
        if method == "write":
            return self.write(value, target)
        if method == "read":
            return self.read()