# HWC representation of Memory
class Memory():
    def __init__(self, size, 
                read, readBit,
                write, writeBit):

        self.size     = size
        self.read     = read
        self.readBit  = readBit
        self.write    = write
        self.writeBit = writeBit

    def __str__(self):
        memStr  = ""
        memStr += "MEMORY:" + "\n"
        memStr += "SIZE: "  + str(self.size) + "\n"
        memStr += "READ: "  + self.read      + "\tREAD_BIT: "  + str(self.readBit)  + "\n"
        memStr += "WRITE: " + self.write     + "\tWRITE_BIT: " + str(self.writeBit) + "\n"

        return memStr