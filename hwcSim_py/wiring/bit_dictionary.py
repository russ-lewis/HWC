class Bit_Dictionary():

    def __init__(self):
        self.dictionary = {}

    def addReader(self, key, value):
        if not key in self.dictionary:
            self.dictionary[key] = BD_Value()
            
        self.dictionary.get(key).addReader(value)
            

    def addWriter(self, key):
        if not key in self.dictionary:
            self.dictionary[key] = BD_Value()
        
        return self.dictionary.get(key).addWriter()

    def __str__(self):
        dictStr =  "BIT DICTIONARY: \n"

        for key in self.dictionary:
            dictStr += str(key) + ":\t " + str(self.dictionary.get(key)) + "\n"

        dictStr += "\n############################################################################\n"

        return dictStr


class BD_Value():

    def __init__(self):
        self.readers = []
        self.writers = False

    def start():
        return

    def reset():
        return

    def addReader(self, value):
        self.readers.append(value)

    def addWriter(self):
        if (self.writers == True):
            return False

        self.writers = True
        return True

    def __str__(self):
        valStr = "[["

        for reader in self.readers:
            valStr += str(reader) + ", "
        
        valStr += "], " + str(self.writers)
        valStr += "]"
        return valStr



        

