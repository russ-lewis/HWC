# HWC representation of the input output gates

class Input():

    def __init__(self, size, name, bit):
        self.size = size
        self.name = name
        self.bit  = bit
    
    def __str__(self):
        ioStr  = ""
        ioStr += "INPUT:" + "\n"
        ioStr += "NAME: " + self.name + "\tBIT: " + str(self.bit) + "\tSIZE: " + str(self.size) + "\n"

        return ioStr


class Output():

    def __init__(self, name):
        self.name = name
        self.val  = None

    def deliver_val(self, val):
        print("OUTPUT DELIVERED: " + str(val))
        self.val = val

    def __str__(self):
        ioStr  = ""
        ioStr += "OUTPUT:" + "\n"
        ioStr += "NAME: " + self.name + "\tBIT: " + str(self.bit) + "\tSIZE: " + str(self.size) + "\n"

        return ioStr