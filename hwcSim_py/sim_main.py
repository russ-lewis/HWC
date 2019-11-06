import sys

from wiring.bit_dictionary import Bit_Dictionary

from wiring.connection import Connection
from wiring.hwcassert  import HWCAssert
from wiring.memory     import Memory
from wiring.logic      import Logic
from wiring.io         import Input
from wiring.io         import Output

def main():

    '''
    Arguments we will support currently:
    Usage: python sim_main.py (--reset) (--genTemplate) (--run <tick_amount>) (--input <file_name>)

    --run <tick_amount>: Sets the simulator to run for <tick_amount> of ticks

    --input <file_name>: Sets the input file for the simulator, file_name supports csv structure

    --reset: Resets the memory and internal bit array

    --genTemplate: generates the input template

    --debug <debug_option>: Stops program after certain debug step and returns the output
    '''

    # If the only argument is the sim_main.py, then return error message
    if (len(sys.argv) < 2):
        print("Correct Usage: python sim_main.py (--reset) (--genTemplate) (--run <tick_amount>) (--input <file_name>)")

    else:
        # Points to the first argument in sys.argv list
        # The pointer moves to the next argument instead of checking total argument length
        arg_ptr = 1

        # Fields to store the values of the optional arguments
        reset           = False
        genTemplate     = False
        tick_count      = 0
        input_filename  = ""
        debug           = 0

        while (arg_ptr < len(sys.argv)):

            # NOT supported right now
            if (sys.argv[arg_ptr] == "--reset"):
                print("Command option '--reset' argument is currently not supported")
                reset = True
                arg_ptr += 1
                continue

            # NOT supported right now
            if (sys.argv[arg_ptr] == "--genTemplate"):
                print("Command option '--genTemplate' argument is currently not supported")
                genTemplate = True
                arg_ptr += 1
                continue

            # Sets the tick amount for the simulator to run
            if (sys.argv[arg_ptr] == "--run"):
                tick_count = sys.argv[arg_ptr + 1]
                arg_ptr += 2
                continue

            # Sets the input file that the simluator will read in
            if (sys.argv[arg_ptr] == "--input"):
                input_filename = sys.argv[arg_ptr + 1]
                arg_ptr += 2
                continue

            # NOT supported right now
            if (sys.argv[arg_ptr] == "--debug"):
                debug = sys.argv[arg_ptr + 1]
                arg_ptr += 2
                continue

            # Additional arguments 

        # Print the argument fields to verify its working
        print("\n############################################################################\n")

        print("Input File:        " + input_filename)
        print("Tick Count:        " + str(tick_count))
        print("Reset:             " + str(reset))
        print("Debug:             " + str(debug))
        print("Generate Template: " + str(genTemplate))

        print("\n############################################################################\n")

    # TODO: read in input files

    '''

    # Open the file
    try:
        file = open(input_filename, "r")

        # Tracking total counts of parts and 
        bits        = 0
        memCount    = 0
        logicCount  = 0
        connCount   = 0
        assertCount = 0

        # Arrays for storing logic, connections, asserts
        logics      = []
        connections = []
        asserts     = []
        memory      = []
        inputs      = []
        outputs     = []

        # Read the first line to initialize while loop
        line  = file.readline()

        while line:
            # Avoid comment lines in .wire files
            if (line[0] == "#"):
                line = file.readline()
                continue

            # Catches empty and new lines
            if (line == "\n" or line == ""):
                line = file.readline()
                continue

            # Extracts total bit size from .wire file
            if (line.startswith("bits")):
                bits = int(line.split()[1])
                line = file.readline()
                continue

            if line.startswith("memory count"):
                memCount = int(line.split()[2])
                memory   = [None] * memCount

                line = file.readline()
                for i in range(int(memCount)):
                    memInfo   = line.strip().split()
                    memory[i] = Memory(int(memInfo[2]),
                                       memInfo[3],
                                       int(memInfo[4]),
                                       memInfo[5],
                                       int(memInfo[6]))
                    
                    line = file.readline()

                print("MEMORY:      {}".format(memory))

            if line.startswith("logic count"):
                logicCount = int(line.split()[2])
                logics     = [None] * logicCount

                line = file.readline()
                for i in range(int(logicCount)):
                    logInfo   = line.strip().split()
                    if logInfo[1] != "NOT":
                        logics[i] = Logic(logInfo[1],
                                        int(logInfo[3]),
                                        logInfo[4],
                                        int(logInfo[5]),
                                        logInfo[6],
                                        int(logInfo[7]),
                                        logInfo[8],
                                        int(logInfo[9]))
                    else:
                        logics[i] = Logic(logInfo[1],
                                        int(logInfo[3]),
                                        logInfo[4],
                                        int(logInfo[5]),
                                        "",
                                        "",
                                        logInfo[6],
                                        int(logInfo[7]))


                    line = file.readline()

                print("LOGIC:       {}".format(logics))

            if line.startswith("connection count"):
                connCount   = int(line.split()[2])
                connections = [None] * connCount

                line = file.readline()
                for i in range(int(connCount)):
                    connInfo       = line.strip().split()
                    connections[i] = Connection(int(connInfo[2]),
                                                connInfo[3],
                                                int(connInfo[4]),
                                                connInfo[5],
                                                int(connInfo[6]))

                    line = file.readline()

                print("CONNECTIONS: {}".format(connections))

            if line.startswith("assert count"):
                assertCount = int(line.split()[2])
                asserts     = [None] * assertCount

                line = file.readline()
                for i in range(int(assertCount)):
                    assertInfo = line.strip().split()
                    asserts[i] = HWCAssert(int(assertInfo[1]))

                    line = file.readline()

                print("ASSERTS:     {}".format(asserts))

            if line.startswith("i/o count"):
                ioCount = int(line.split()[2])

                line = file.readline()
                for i in range(int(ioCount)):
                    ioInfo = line.strip().split()

                    if ioInfo[0] == "input":
                        inputs.append(Input(
                                      int(ioInfo[2]),
                                      ioInfo[3],
                                      int(ioInfo[4])))

                    elif ioInfo[0] == "output":
                        outputs.append(Output(
                                       int(ioInfo[2]),
                                       ioInfo[3],
                                       int(ioInfo[4])))

                    else:
                        print(line)
                        print("ERROR: wire file was not readable")
                        exit(1)
                        # Throw error

                    line = file.readline()

                print("INPUTS:      {}".format(inputs))
                print("OUTPUTS:     {}".format(outputs))

            line = file.readline()

        # END while loop

        file.close()

        # Print the argument fields to verify its working
        print("\n############################################################################\n")

        print("TOTAL BITS: " + str(bits) + "\n")

        print("MEMORY OBJECT COUNT: " + str(memCount))
        for mem in memory:
            print(mem)
        print("")

        print("LOGIC OBJECT COUNT: " + str(logicCount))
        for logic in logics:
            print(logic)
        print("")

        print("CONNECTION OBJECT COUNT: " + str(connCount))
        for connection in connections:
            print(connection)
        print("")

        print("ASSERT OBJECT COUNT: " + str(assertCount))
        for hwcassert in asserts:
            print(hwcassert)
        print("")

        print("INPUT OBJECT COUNT: " + str(len(inputs)))
        for hwcInput in inputs:
            print(hwcInput)
        print("")

        print("OUTPUT OBJECT COUNT: " + str(len(outputs)))
        for hwcOutput in outputs:
            print(hwcOutput)
        print("")
        
        print("\n############################################################################\n")

    except IOError:
        print("ERROR: Unable to find or open " + input_filename)
        exit(1)

    '''

    # TODO: build the object graph

    '''
    Dictionary Structure

    The bit dictionary holds all internal bits and what their connections are. This is used to
    ultimately build the graph data structure that will be used to model the circuitry. The format
    of the dictionary maps bit ranges to read and write values.

    Bit Dictionary Representation:
    +---------------------------------------+
    |   Bit     |   Read    |   Write       |
    |   --------|-----------|-----------    |  
    |   (0,1)   |   [a]     |   FALSE       |
    |   (1,2)   |   [a,b]   |               |
    |   (2,5)   |   [NOT]   |               |
    |   (6,7)   |   []      |               |
    +---------------------------------------+

    INVARIANT: If there is no write, then output

    '''

    # Steps
    # 1. Find the bit ranges
    # 2. Add read and write values depending on line
    # 3. Collapse fan out and fan in connections

    bit_dictionary = Bit_Dictionary()

    try:
        # Open the file
        file = open(input_filename, "r")

        # Initializa bit dictionary using Python built in dictionary
        # Store read-write values in an array for now
        # TODO: Make a custom data structure to model READ-WRITE?
        # TODO: Make a custom data structure to model this?
        
        # Read the first line to initialize while loop
        line = file.readline()

        while line:
            # Avoid comment lines in .wire files
            if (line[0] == "#"):
                line = file.readline()
                continue

            # Catches empty and new lines
            if (line == "\n" or line == ""):
                line = file.readline()
                continue

            # Extracts total bit size from .wire file
            if (line.startswith("bits")):
                bits = int(line.split()[1])
                line = file.readline()
                continue

            # Adds logics to the bit dictionary
            if line.startswith("logic count"):
                logicCount = int(line.split()[2])

                line = file.readline()
                for logic in range(logicCount):
                    logicInfo = line.split()
                    
                    if (logicInfo[1] == "NOT"):
                        size = int(logicInfo[3])
                        a    = int(logicInfo[5])
                        out  = int(logicInfo[7])
                        
                        bit_dictionary.addReader((a, size), out)
                        bit_dictionary.addWriter((out, size))

                    else:
                        size = int(logicInfo[3])
                        a    = int(logicInfo[5])
                        b    = int(logicInfo[7])
                        out  = int(logicInfo[9])

                        bit_dictionary.addReader((a, size), out)
                        bit_dictionary.addReader((b, size), out)
                        bit_dictionary.addWriter((out, size))

                    line = file.readline()

                continue

            # Adds connections to the bit dictionary
            if line.startswith("connection count"):
                connCount = int(line.split()[2])

                line = file.readline()
                for conn in range(connCount):
                    connInfo = line.split()
                    
                    size    = int(connInfo[2])
                    toBit   = int(connInfo[4])
                    fromBit = int(connInfo[6])

                    bit_dictionary.addReader((fromBit, size), toBit)
                    bit_dictionary.addWriter((toBit, size))

                    line = file.readline()

                continue

            # Adds i/o counts to the bit dictionary
            if line.startswith("i/o count"):
                ioCount = int(line.split()[2])

                line = file.readline()
                for io in range(ioCount):
                    ioInfo = line.split()
                    
                    if (ioInfo[0] == "input"):
                        size  = int(ioInfo[2])
                        inBit = int(ioInfo[4])

                        bit_dictionary.addReader((inBit, size), "INPUT")
                    else:
                        size   = int(ioInfo[2])
                        outBit = int(ioInfo[4])

                        bit_dictionary.addWriter((outBit, size))

                    line = file.readline()

                continue

            line = file.readline()

        file.close()

    except IOError:
        print("ERROR: Unable to find or open " + input_filename)
        exit(1)

    print(bit_dictionary)

    # TODO: Build the lambdas to deliver the values
    

    



main()