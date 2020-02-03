# Assert representation in HWC

class HWCAssert():

    def __init__(self, inBit):
        self.output = inBit

    def setInBit(self, inBit):
        self.inBit = inBit

    def getInBit(self):
        return self.inBit

    def evaluateAssert(self):
        return True

    def __str__(self):
        assertStr  = ""
        assertStr += "ASSERT:\n"
        assertStr += "INBIT: " + str(self.inBit) + "\tVALUE: " + evaluateAssert() + "\n"

        return assertStr