class Device:
    FLOW_IN = 0
    FLOW_OUT = 1

    def __init__(self, name, port, flow):
        self.name = name
        self.port = port
        self.flow = flow
        self.value = 0
        self.dirty = False
    
    def getName(self):
        return self.name

    def getPort(self):
        return self.port

    def getFlow(self):
        return self.flow

    def setValue(self, value):
        self.value = value
        self.dirty = True

    def isDirty(self):
        return self.dirty

    def clean(self):
        self.dirty = False

    def getValue(self):
        return self.value

    def toString(self):
        return self.getName() + " (" + str(self.getPort()) + ") : " + str(self.getValue())
