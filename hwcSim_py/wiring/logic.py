# Logic Gate representation in HWC

class Logic():

    def __init__(self, opType, size,
                 plugA, plugABit,
                 plugB, plugBBit,
                 plugOut, plugOutBit):

        self.size       = size
        self.opType     = opType
        self.plugA      = plugA
        self.plugABit   = plugABit
        self.plugB      = plugB
        self.plugBBit   = plugBBit
        self.plugOut    = plugOut
        self.plugOutBit = plugOutBit

    def __str__(self):
        logStr  = ""
        logStr += "LOGIC:\n"
        logStr += "SIZE: " + str(self.size) + "\tOP: "  + self.opType          + "\n"
        logStr += "FROM: " + self.plugA     + "\tBIT: " + str(self.plugABit)   + "\n"
        logStr += "TO:   " + self.plugB     + "\tBIT: " + str(self.plugBBit)   + "\n"
        logStr += "OUT:  " + self.plugOut   + "\tBIT: " + str(self.plugOutBit) + "\n" 

        return logStr
