class Bit_Dictionary():

    def __init__(self):
        self.dictionary = {}

    def addReader(self, key, value):
        if not key in self.dictionary:
            self.dictionary[key] = BD_Value()

        # Doesnt add a reader if memory
        if not value == None:   
            self.dictionary.get(key).addReader(value)

    def get(self, key):
        return self.dictionary.get(key)

    def addWriter(self, key):
        if not key in self.dictionary:
            self.dictionary[key] = BD_Value()
        
        return self.dictionary.get(key).addWriter()

    def get_readers(self, key):
        return self.dictionary.get(key).get_readers()

    def get_writers(self, key):
        return self.dictionary.get(key).get_writers()

    def get_test_str(self):
        dictStr =  "BIT DICTIONARY: \n"

        # Depending on the size of the Bit array, may have to change.
        # Sorting algorithm might have ridiculuous time cost
        for key in sorted(self.dictionary.keys(), key=lambda x: x[0]):
            dictStr += str(key) + ":\t[" + str(len(self.dictionary.get(key).get_readers())) + ", " + str(self.dictionary.get(key).get_writers()) + "]\n"

        dictStr += "\n############################################################################\n"

        return dictStr

    def __str__(self):
        dictStr =  "BIT DICTIONARY: \n"

        # Depending on the size of the Bit array, may have to change.
        # Sorting algorithm might have ridiculuous time cost
        for key in sorted(self.dictionary.keys(), key=lambda x: x[0]):
            dictStr += str(key) + ":\t" + str(self.dictionary.get(key)) + "\n"

        dictStr += "\n############################################################################\n"

        return dictStr


class BD_Value():

    def __init__(self):
        self.readers = []
        self.writers = False

    def addReader(self, value):
        self.readers.append(value)

    def addWriter(self):
        if (self.writers == True):
            return False

        self.writers = True
        return True

    def get_readers(self):
        return self.readers

    def get_writers(self):
        return self.writers

    def __str__(self):
        valStr = "[["

        for reader in self.readers:
            valStr += str(reader) + ", "
        
        # Hacky way to fencepost the string if not empty list
        if (self.readers != []):
            valStr = valStr[:-2]

        valStr += "], " + str(self.writers)
        valStr += "]"
        return valStr



        

