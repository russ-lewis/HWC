class LogicOp(object):

    def __init__(self, readers, writers, name):
        self.readers = readers
        self.writers = writers
        self.name    = name

    def getName(self):
        return self.name

    def getReaders(self):
        return self.readers
    
    def getWriters(self):
        return self.writers

    def __str__(self):
        logic_str = ""
        
        logic_str += "NAME:    " + self.name         + "\n"
        logic_str += "READERS: " + str(self.readers) + "\n"
        logic_str += "WRITERS: " + str(self.writers) + "\n"
        
        return logic_str


class NOT(LogicOp):

    def __init__(self, readers, writers, name):
        LogicOp.__init__(self, readers, writers, name)

        self.val_a = None
        self.out   = None

    def deliver_a(self, val):
        self.val_a = val

        # try to evaluate operation
        self.evaluate_op()

    def evaluate_op(self):
        if self.val_a == None or self.out != None:
            return

        if self.val_a == 1:
            self.out = 0
    
        elif self.val_a == 0:
            self.out = 1

        else:   # Catch unexpected behavior
            return

        for reader in self.readers:
            reader(self.out)


    def get_lambda(self):
        return lambda val: deliver_a(val)


class AND(LogicOp):

    def __init__(self, readers, writers, name):
        LogicOp.__init__(self, readers, writers, name)

        self.val_a = None
        self.val_b = None
        self.out   = None

    def deliver_a(self, val):
        self.val_a = val

    def deliver_b(self, val):
        self.val_b = val

    def deliver_a(self, val):
        self.val_a = val

        # try to evaluate operation
        self.evaluate_op()

    def evaluate_op(self):
        if self.val_a == None or self.val_b == None or self.out != None:
            return

        val = self.val_a + self.val_b

        # True if both 0 or both 1
        if val == 0 or val == 2:
            self.out = 1
        else:
            self.out = 0

        for reader in self.readers:
            reader(self.out)

    def get_lambda():
        return