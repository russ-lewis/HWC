import sys

from wiring.bit_dictionary import Bit_Dictionary

from wiring.connection import Connection
from wiring.hwcassert  import HWCAssert
from wiring.memory     import Memory
from wiring.logic      import Logic
from wiring.io         import Input
from wiring.io         import Output

from wiring.logic_ops  import *

bit_dictionary = Bit_Dictionary()

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
        wire_filename   = ""
        input_filename  = ""
        debug           = 0
        auto            = False

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

            if (sys.argv[arg_ptr] == "--wire"):
                wire_filename = sys.argv[arg_ptr + 1]
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

            # TODO: Auto gen input
            if (sys.argv[arg_ptr] == "--auto"):
                auto = True
                arg_ptr += 1
                continue

            # Additional arguments 

        # Print the argument fields to verify its working
        print("\n############################################################################\n")

        print("Wire File:         " + wire_filename)
        print("Input File:        " + input_filename)
        print("Tick Count:        " + str(tick_count))
        print("Reset:             " + str(reset))
        print("Debug:             " + str(debug))
        print("Generate Template: " + str(genTemplate))
        print("Auto:              " + str(auto))

        print("\n############################################################################\n")

    # TODO: read in input files
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
    |   [0,1]   |   [a]     |   c           |
    |   [1,2]   |   [a,b]   |               |
    |   [2,5]   |   [NOT]   |               |
    |   [6,7]   |   []      |               |
    +---------------------------------------+

    INVARIANT: If there is no write, then output

    '''

    # Steps
    # 1. Find the bit ranges
    # 2. Add read and write values depending on line
    # 3. Collapse fan out and fan in connections


    # TODO: CHANGES
    # TODO: Create objects for LogicOps (NOT, AND, etc)
    # TODO: Change order of parsing to, output side first
    # TODO: Lambdas for the connections

    try:
        # Open the file
        file = open(wire_filename, "r")

        # Initializa bit dictionary using Python built in dictionary
        # Store read-write values in an array for now
        # TODO: Make a custom data structure to model READ-WRITE?
        # TODO: Make a custom data structure to model this?
        
        outputs = []
        inputs  = []

        logic_ops = {}
        
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

            if line.startswith("logic count"):
                logicCount = int(line.split()[2])

                line = file.readline()
                for logic in range(logicCount):
                    logicInfo = line.split()
                    
                    if (logicInfo[1] == "NOT"):
                        size = int(logicInfo[3])
                        a    = int(logicInfo[5])
                        out  = int(logicInfo[7])

                        # Build keys for dictionary
                        reader_a_key = (a  , size)
                        writer_key   = (out, size)

                        # Parse "to" bit
                        result = bit_dictionary.addWriter(writer_key)

                        if not result:
                            print("Short circuit detected @ " + line)
                            exit(1)

                        # Create NOT Object for LogicOp
                        not_obj = NOT(bit_dictionary.get_readers(writer_key), 
                                      bit_dictionary.get_writers(writer_key), 
                                      "NOT-" + str(writer_key))

                        # Parse from side
                        bit_dictionary.addReader(reader_a_key, lambda val: not_obj.deliver_a(val))

                        logic_ops[not_obj.getName()] = not_obj

                    else:
                        size = int(logicInfo[3])
                        a    = int(logicInfo[5])
                        b    = int(logicInfo[7])
                        out  = int(logicInfo[9])

                        # Build keys for dictionary
                        reader_a_key = (a  , size)
                        reader_b_key = (b  , size)
                        writer_key   = (out, size)

                        # Parse "to" bit
                        result = bit_dictionary.addWriter(writer_key)

                        if not result:
                            print("Short circuit detected @ " + line)
                            exit(1)

                        if logicInfo[1] == "AND":
                            # Create AND Object for LogicOp
                            logic_obj = AND(bit_dictionary.get_readers(writer_key), 
                                        bit_dictionary.get_writers(writer_key), 
                                        "AND-" + str(writer_key))

                        elif logicInfo[1] == "OR":
                            # Create AND Object for LogicOp
                            logic_obj = OR(bit_dictionary.get_readers(writer_key), 
                                        bit_dictionary.get_writers(writer_key), 
                                        "OR-" + str(writer_key))

                        elif logicInfo[1] == "XOR":
                            # Create AND Object for LogicOp
                            logic_obj = XOR(bit_dictionary.get_readers(writer_key), 
                                        bit_dictionary.get_writers(writer_key), 
                                        "XOR-" + str(writer_key))

                        else:
                            print("ERROR: Logic object not yet supported")
                            exit(1)

                        # Parse from side
                        bit_dictionary.addReader(reader_a_key, lambda val: logic_obj.deliver_a(val))
                        bit_dictionary.addReader(reader_b_key, lambda val: logic_obj.deliver_b(val))

                        logic_ops[logic_obj.getName()] = logic_obj

                    line = file.readline()

                continue

            if line.startswith("connection count"):
                connCount = int(line.split()[2])

                line = file.readline()
                for conn in range(connCount):
                    connInfo = line.split()
                    
                    size    = int(connInfo[2])
                    toBit   = int(connInfo[4])
                    fromBit = int(connInfo[6])

                    reader_key = (fromBit, size)
                    writer_key = (toBit  , size)

                    # Parse "to" side
                    result = bit_dictionary.addWriter(writer_key)

                    if not result:
                        print("Short circuit detected @ " + line)
                        exit(1)

                    # Parse from side
                    bit_dictionary.addReader(reader_key, make_conn(writer_key))

                    line = file.readline()

                continue

            if line.startswith("i/o count"):
                ioCount = int(line.split()[2])

                line = file.readline()
                for io in range(ioCount):
                    ioInfo = line.split()
                    
                    if (ioInfo[0] == "input"):
                        size  = int(ioInfo[2])
                        inBit = int(ioInfo[4])

                        writer_key = (inBit, size)

                        bit_dictionary.addWriter(writer_key)
                        inputs.append(writer_key)

                        if not result:
                            print("Short circuit detected @ " + line)
                            exit(1)

                    else:
                        size   = int(ioInfo[2])
                        outBit = int(ioInfo[4])

                        reader_key = (outBit, size)
                        output_obj = Output("OUT-" + str(reader_key))

                        # THIS IS WEIRD:
                        # So print(x) works on Windows but it doesnt work on Mac
                        # sys.stdout.write(x) works on Mac though
                        #
                        # https://stackoverflow.com/questions/2970858/why-doesnt-print-work-in-a-lambda
                        bit_dictionary.addReader(reader_key, lambda val: sys.stdout.write("OUTPUT: " + str(val) + "\n")) #lambda val: output_obj.deliver_val(val))
                        outputs.append(reader_key)

                    line = file.readline()

                continue

            line = file.readline()

        if (auto):
            print(bit_dictionary.get_test_str())
        else:
            print(bit_dictionary)

            for logic_op in logic_ops:
                print(logic_ops[logic_op])

        print("INPUTS: ")

        for input_bit in inputs:
            print(input_bit)

        print("OUTPUTS: ")

        for output in outputs:
            print(output)

        print("\n############################################################################\n")

    except IOError:
        print("ERROR: Unable to find or open " + input_filename)
        exit(1)

    # TODO: write the simiulation algorithm of propegating bits
    # Run the simulation

    user_inputs = {}

    # AUTO FLAG: used for testing through test script 

    # Relistically we should test all possible single bit inputs to determine if the program actually works
    # BUT: for now I'm going to only test single bits -> 1
    if (auto):
        for hwc_input in inputs:
            
            user_inputs[hwc_input] = 1

            assert user_inputs[hwc_input] >= 0
            assert user_inputs[hwc_input] <  2**(hwc_input[1])    # TODO: report an error to the user, not assert!

        # TODO: Drive rest of bits off input
        # Follow until an output is reached
        for user_in in user_inputs:
            readers = bit_dictionary.get(user_in).get_readers()

            for reader in readers:
                reader(user_inputs.get(user_in))

    else:
        # TODO: Get input from user input
        for hwc_input in inputs:
            
            user_inputs[hwc_input] = int(input("Enter input for " + str(hwc_input) + ": "))

            '''
            assert user_inputs[hwc_input] >= 0
            assert user_inputs[hwc_input] <  2**(hwc_input[1])    # TODO: report an error to the user, not assert!
            '''

        # TODO: Drive rest of bits off input
        # Follow until an output is reached
        for user_in in user_inputs:

            readers = bit_dictionary.get(user_in).get_readers()

            for reader in readers:
                reader(user_inputs.get(user_in))

    # TODO: Show output



# Needed to lock values when using lambda
def make_conn(writer_key):
    return lambda val: [reader(val) for reader in bit_dictionary.get_readers(writer_key)]

main()
