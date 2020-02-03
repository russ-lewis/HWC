# HWC representation of Memory
class Memory(object):
    def __init__(self, size, readers, writers, value):

        self.size    = size
        self.value   = value
        self.readers = readers
        self.writers = writers

    def get_value(self):
        return self.value

    def get_readers(self):
        return self.readers

    def get_writers(self):
        return self.writers

    def deliver_val(self, val):
        # Needs to pass value stored in mem to its readers.
        for reader in self.readers:
            reader(val)

    def __str__(self):
        mem_str  = ""

        mem_str += "MEMORY:" + "\n"
        mem_str += "SIZE: "  + str(self.size) + "\n"
        mem_str += "READ: "  + self.readers   + "\n"
        mem_str += "WRITE: " + self.writeers  + "\n"

        return memStr

    