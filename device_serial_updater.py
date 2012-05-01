import time
import serial
from device import Device
from threading import Thread

class DeviceSerialUpdater(Thread):
    def __init__(self, devices):
        Thread.__init__(self)
        self.serial_link = serial.Serial('/dev/ttyUSB0', 115200)
        self.send_buffer = bytearray(1)
        self.devices = devices
        self.daemon = True

    def getDevices():
        return self.devices

    def setDevices(devices):
        self.devices = devices 

class DeviceSerialPush(DeviceSerialUpdater):
    def setStatus(self, port, status):
        self.send_buffer[0] = (status << 7) | port
        self.serial_link.write(self.send_buffer)

    def updateDevices(self):
        for d in self.devices:
            if d.getFlow() == Device.FLOW_OUT and d.isDirty():
                self.setStatus(d.getPort(), d.getValue())
                d.clean()

    def run(self):
        while 1:
            #print "pushing..."
            self.updateDevices()
            time.sleep(.01)
    
class DeviceSerialPull(DeviceSerialUpdater):
    def updateStatus(self, port, value):
        for d in self.devices:
            if d.getFlow() == Device.FLOW_IN and d.getPort() == port:
                d.setValue(value)
        
    def pullStatus(self):
        line = self.serial_link.readline()
        a = line.split(':', 1)
        try:
            port = int(a[0]) # danger zone!
            value = int(a[1])
            self.updateStatus(port, value)
        except:
            print "bad pull data: '" + line + "'"


    def run(self):
        while 1:
            #print "pulling..."
            self.pullStatus()
            #time.sleep(.1)
        

