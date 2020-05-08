# Models connections in HWC

class Connection():

    def __init__(self, size, toPlug, toPlugBit, fromPlug, fromPlugBit):
        self.size        = size
        self.fromPlug    = fromPlug
        self.fromPlugBit = fromPlugBit
        self.toPlug      = toPlug
        self.toPlugBit   = toPlugBit
        

    def setSize(self, size):
        self.size = size

    def getSize(self):
        return self.size

    def setFromPlug(self, fromPlug):
        self.fromPlug = fromPlug

    def getFromPlug(self):
        return self.fromPlug

    def setFromPlugBit(self, fromPlugBit):
        self.fromPlug = fromPlugBit

    def getFromPlugBit(self):
        return self.fromPlugBit

    def setToPlug(self, toPlug):
        self.toPlug = toPlug

    def getToPlug(self):
        return self.toPlug

    def setToPlugBit(self, toPlugBit):
        self.toPlug = toPlugBit

    def getToPlugBit(self):
        return self.toPlugBit

    def __str__(self):
        connStr  = "CONNECTION:\n"
        connStr += "SIZE: " + str(self.size) + "\n"
        connStr += "FROM: " + self.fromPlug  + "\tBIT: " + str(self.fromPlugBit) + "\n"
        connStr += "TO:   " + self.toPlug    + "\tBIT: " + str(self.toPlugBit  ) + "\n"

        return connStr