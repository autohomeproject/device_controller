import time
import pg
from rules import *
from device import *
from device_serial_updater import *

aset = ActionSet(1)
aset.actions = []
cset = ConditionSet(1)
cset.conditions = []
devices = []

for i in range(1,6):
    name = 'led' + str(i)
    port = 8 + i
    a = Action(i, name, 0, 1) # id, name, duration, value
    aset.actions.append(a)
    d = Device(name, port, Device.FLOW_OUT)
    devices.append(d)


name = 'light1'
port = 16
c = Condition(1, name, Condition.C_LT, 100)
cset.conditions.append(c)
ls = Device(name, port, Device.FLOW_IN)
devices.append(ls)

con = pg.connect('autohome_development', 'menlohotels.com', 5432, None, None, 'autohome', 'autohome')

try:
    dss = DeviceSerialPush(devices);
    dsl = DeviceSerialPull(devices);
    dss.start()
    dsl.start()
except (KeyboardInterrupt, SystemExit):
    print '\n! Received keyboard interrupt, quitting threads.\n'
    sys.exit()


rs = RuleSet(1)
rs.condition_set = cset
rs.action_set = aset

while 1:
    if rs.execute(devices) == True:
        pass
    else:
        for d in devices:
            if d.getFlow() == Device.FLOW_OUT:
                d.setValue(0)

    for d in devices:
        if d.getFlow() == Device.FLOW_IN:
            print d.toString()
    time.sleep(.1)

