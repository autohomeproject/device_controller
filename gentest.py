import time
import pg
from rules import *
from device import *
from device_serial_updater import *

def rslprint(rsl):
    print rsl
    for r in rsl:
        print r.condition_set
        print r.condition_set.conditions
        for c in r.condition_set.conditions:
            print c.device_name + " : " + str(c.comparison) + " | " + str(c.value)
        print r.action_set
        print r.action_set.actions
        for a in r.action_set.actions:
            print a.device_name

devices = []

for i in range(5):
    name = 'led' + str(i)
    port = 9 + i
    d = Device(name, port, Device.FLOW_OUT)
    devices.append(d)


name = 'light1'
port = 16
ls = Device(name, port, Device.FLOW_IN)
devices.append(ls)

#q = con.query('select * from "rule_sets" where id=7')
#r = q.dictresult()
#print "Active?  :  " + r[0]['active']

try:
    dss = DeviceSerialPush(devices);
    dsl = DeviceSerialPull(devices);
    rst = RuleSetTracker()
    dss.start()
    dsl.start()
    rst.start()
except (KeyboardInterrupt, SystemExit):
    print '\n! Received keyboard interrupt, quitting threads.\n'
    sys.exit()


while 1:
    rst.evaluate(devices)
    for d in devices:
        if d.getFlow() == Device.FLOW_IN:
            pass
            #print d.toString()
    time.sleep(.1)


