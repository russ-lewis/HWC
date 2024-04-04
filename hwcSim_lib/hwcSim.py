#! /usr/bin/python3

import sys

import types     # for SimpleNamespace



class HWCSim:
    def __init__(self, infile):
        self.bit_count = 0
        self.names       = []
        self.conns       = []
        self.cond_conns  = []
        self.logic       = []
        self.memory      = []

        while True:
            line = infile.readline().strip()
            if line == "":
                break

            # TODO: record the information for the future

            words = line.split()
            assert words[0] == "#"

            start_bit = int(words[1])
            assert start_bit == self.bit_count

            if words[2][0] in "123456789":
                assert len(words) == 4
                end_bit = int(words[2])
                name    = words[3]
            else:
                assert len(words) == 3
                end_bit = start_bit+1
                name    = words[2]

            self.bit_count = end_bit
            self.names.append( (start_bit,end_bit, name) )

        while True:
            line = infile.readline().split()
            if len(line) == 0:
                break

            if line[0] == "conn":
                to_bit   = int(line[1])
                assert line[2] == "<="
                from_bit = int(line[3])
                assert line[4] == "size"
                size     = int(line[5])

                if line[6] != "cond":
                    assert   to_bit+size <= self.bit_count
                    assert from_bit+size <= self.bit_count
                    self.conns.append( Connection(to_bit,from_bit, size) )

                else:
                    cond = int(line[7])
                    TODO()    # add conditional connection

            elif line[0] == "mem":
                assert line[1] == "r"
                rd = int(line[2])
                assert line[3] == "w"
                wr = int(line[4])
                assert line[5] == "size"
                size = int(line[6])
                assert wr == rd+size
                assert rd+size*2 <= self.bit_count
                self.memory.append(Memory(rd,size))

            elif line[0] == "logic":
                to_bit = int(line[1])
                assert line[2] == "<="

                if line[3] == "NOT":
                    from_bit = int(line[4])
                    assert line[5] == "size"
                    size     = int(line[6])
                    assert   to_bit+size <= self.bit_count
                    assert from_bit+size <= self.bit_count
                    self.logic.append( Logic_NOT(to_bit,from_bit, size) )

                else:
                    print(line[3])
                    print(line[4])
                    TODO()    # other operation

    def dump(self):
        print(f"bit_count: {self.bit_count}")

        print("---- Names ----")
        for n in self.names:
            print(f"{n[0]} {n[1]} {n[2]}")

        print("---- Unconditional Connections ----")
        for c in self.conns:
            c.dump()

        print("---- Conditional Connections ----")
        for c in self.cond_conns:
            c.dump()

        print("---- Logic ----")
        for l in self.logic:
            l.dump()

        print("---- Memory ----")
        for m in self.memory:
            m.dump()

    def run(self):
        init_memory = []
        for m in self.memory:
            init_memory.append( Bits(m.size, 0) )
        return HWCSim_ClockCycle(self, init_memory)



class Memory:
    def __init__(self, rd,size):
        self.rd   = rd
        self.size = size

    def dump(self):
        print(f"rd {self.rd} size {self.size}")



class Connection:
    def __init__(self, to_bit,from_bit, size):
        self.to_bit   = to_bit
        self.from_bit = from_bit
        self.size     = size

    def dump(self):
        print(f"to {self.to_bit} from {self.from_bit} size {self.size}")



class Logic_NOT:
    def __init__(self, to_bit,from_bit, size):
        self.to_bit   = to_bit
        self.from_bit = from_bit
        self.size     = size

    def dump(self):
        print(f"to {self.to_bit} from {self.from_bit} size {self.size} op NOT")



class Bits:
    def __init__(self, size,val):
        self.size = size
        self.val  = val



class HWCSim_ClockCycle:
    def __init__(self, wiring, mem_in):
        self.wiring = wiring
        self.mem_in = mem_in

        self.bits = types.SimpleNamespace()
        self.bits.asdf = "ASDF"
        self.bits.foo  = types.SimpleNamespace()
        self.bits.foo.bar = types.SimpleNamespace()
        self.bits.foo.bar.baz = "FOO.BAR.BAZ"



if __name__ == "__main__":
    model = HWCSim(sys.stdin)
    model.dump()

    clock = model.run()

    print(clock.bits)
    print(clock.bits.asdf)
    print(clock.bits.foo.bar.baz)

