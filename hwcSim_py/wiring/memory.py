# HWC representation of Memory
class Memory(object):
    def __init__(self, size):

        self.size    = size
        self.readers = []
        self.writers = False

        # Instantiate to 0 as defualt
        # Need to probably change to a bit array, that has 0s and 1s
        self.out_val = 0 # Value stored, passed when called
        self. in_val = 0 # Value that will overwrite the stored (reader) val

    def get_value(self):
        return self.out_val

    def get_readers(self):
        return self.readers

    def set_readers(self, readers):
        self.readers = readers

    def get_writers(self):
        return self.writers

    def set_writers(self, writers):
        self.writers = wrtiers

    def deliver_stored_val(self):
        # Needs to pass value stored in mem to its readers.
        for reader in self.readers:
            reader(self.out_val)

    def __str__(self):
        mem_str  = ""

        mem_str += "MEMORY:" + "\n"
        mem_str += "SIZE: "  + str(self.size) + "\n"
        mem_str += "READ: "  + str(self.readers)   + "\n"
        mem_str += "WRITE: " + str(self.writers)  + "\n"

        return mem_str

    