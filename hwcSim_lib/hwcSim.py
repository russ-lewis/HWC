#! /usr/bin/python3

import sys
import types     # for SimpleNamespace



class HWCSim:
    def __init__(self, infile):
        self.bit_count = 0

        self.names = {}
        def add_name(start,end, name):
            words = name.split('.')

            cur = self.names
            for word in words[:-1]:
                if word not in cur:
                    cur[word] = {}
                cur = cur[word]

            last = words[-1]
            assert last not in cur
            cur[last] = (start,end)

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
            add_name(start_bit,end_bit, name)

        self.conns      = []
        self.cond_conns = []
        self.logic      = []
        self.memory     = []

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

    def first_state(self):
        init_memory = [ Bits(m.size, 0) for m in self.memory ]
        return HWCSim_ClockCycle(self, init_memory)



class Bits:
    def __init__(self, size,val, mask=None):
        assert val >= 0
        assert val >> size == 0
        if mask is not None:
            mask >> size == 0

        self.size = size
        self.val  = val
        self.mask = mask



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

    def add_watch(self, cycle):
        # used to prevent multiple-connection
        delivered = False

        def watch_callback(force=False):
            val = cycle.read_bits(self.from_bit, self.size)
            assert type(val) == Bits

            if val.mask is not None:
                TODO()

            nonlocal delivered
            if delivered:
                return

            delivered = True
            cycle.set_bits(self.to_bit, self.size, val)

        cycle.add_watch(self.from_bit, self.size, watch_callback)



class Logic_NOT:
    def __init__(self, to_bit,from_bit, size):
        self.to_bit   = to_bit
        self.from_bit = from_bit
        self.size     = size

    def dump(self):
        print(f"to {self.to_bit} from {self.from_bit} size {self.size} op NOT")



class HWCSim_ClockCycle:
    def __init__(self, wiring, mem_in):
        self.wiring = wiring

        print("TODO: make this a tree, with ranges at the leaves and watches registered at every level.")
        self.bit_space = [ [0, self.wiring.bit_count, None, []] ]

        for c in self.wiring.conns:
            c.add_watch(self)
        for c in self.wiring.cond_conns:
            c.add_watch(self)
        for l in self.wiring.logic:
            l.add_watch(self)
        for m in self.wiring.memory:
            m.add_watch(self)

        assert len(mem_in) == len(self.wiring.memory)
        for i in range(len(mem_in)):
            size = mem_in[i].size
            val  = mem_in[i].val

            assert self.wiring.memory[i].size == size
            rd = self.wiring.memory[i].rd
            wr = rd+size

            self.set_bits(rd,size, val)

        self.fields = Fields(self, self.wiring.names)

    def set_bits(self, dest,size, val):
        print("TODO: add set-records for each call, which include dependency-records, so that we can replay the tree of actions in a different order in a GUI")

        assert dest >= 0
        assert dest+size <= self.wiring.bit_count
        assert val.val >> size == 0

        indx = self.find_indx_for_range(dest,size, split=True)
        assert self.bit_space[indx][0] == dest
        assert self.bit_space[indx][1] <= size

        if self.bit_space[indx][1] != size:
            TODO()

        if self.bit_space[indx][2] is not None:
            raise HWCRuntime_MultipleConnectionError()
        self.bit_space[indx][2] = val

        for start,size,cb in self.bit_space[indx][3]:
            cb()

    def find_indx_for_range(self, dest,size, split=True):
        assert dest+size <= self.wiring.bit_count

        if split:
            retval = self.split_bits_at(dest)
            self.split_bits_at(dest+size)

        return retval

    def split_bits_at(self, dest):
        a = 0                      # left  index, inclusive
        b = len(self.bit_space)    # right index, exclusive

        while True:
            assert a <= b
            m = (a+b)//2

            start = self.bit_space[m][0]
            end   = self.bit_space[m][0] + self.bit_space[m][1]

            if start == dest:
                return m      # NOP
            if end == dest:
                return m+1    # NOP

            if dest < start:
                b = m
                continue
            if end < dest:
                a = m
                continue

            # dest is inside the current range!

            old_val = self.bit_space[m][2]
            assert old_val is None, old_val    # TODO: handle int's

            print("TODO: split the watchers!")
            part1 = [start,(dest-start), None, self.bit_space[m][3]]
            part2 = [dest ,(end -dest ), None, self.bit_space[m][3]]

            self.bit_space = self.bit_space[:m] + [part1,part2] + self.bit_space[m+1:]

    def read_bits(self, start,size):
        for entry in self.bit_space:
            if entry[0] == start and entry[1] == size:
                val = entry[2]
                assert type(entry[2]) == Bits, entry     # TODO: handle more complex things
                return val
        assert False, (start,size)    # TODO: handle reads that cross ranges
            
    def add_watch(self, dest,size, callback):
        assert len(self.bit_space) == 1
        assert     self.bit_space[0][0] == 0
        assert     self.bit_space[0][1] == self.wiring.bit_count
        self.bit_space[0][3].append( (dest,size,callback) )

    def get_mem_out(self):
        retval = []
        for m in self.wiring.memory:
            TODO()    # read the value into the array we'll return.  Make sure to collect from the write-side if set, and the read-side only for bits that didn't change
        return retval

    def tick(self, inputs={}):
        retval = self.next()
        for k in inputs:
            retval.set(k, inputs[k])
        retval.run()
        return retval

    def next(self):
        return HWCSim_ClockCycle(self.wiring, self.get_mem_out())

    def run(self):
        print("TODO: eventually, support a backlog of recorded (but not called) callbacks that include mask fields.  Only call them when the other (non-lazy) operations are done.  Maybe make *all* of the callbacks lazy???")



class Fields:
    def __init__(self, cur_clock, names):
        assert type(names) == dict

        # we need to make sure that these 
        super(Fields,self).__setattr__("Fields_clock", cur_clock)
        super(Fields,self).__setattr__("Fields_names", names)

    def __getattr__(self, name):
        if name not in self.Fields_names:
            print(name, self.Fields_names)
            raise AttributeError()

        retval = self.Fields_names[name]

        if type(retval) == dict:
            retval = Fields(self.Fields_clock, retval)
            super(Fields,self).__setattr__(name, retval)
            return retval

        else:
            start = retval[0]
            size  = retval[1]-retval[0]

            retval = self.Fields_clock.read_bits(start,size)

            assert type(retval) == Bits
            if retval.mask is None:
                return retval.val

            TODO()    # how to handle masks???

    def __setattr__(self, name, val):
        assert type(val) == int

        if name not in self.Fields_names:
            print(name, self.Fields_names)
            raise AttributeError()

        thing = self.Fields_names[name]
        if type(thing) == dict:
            TODO()    # should I report AttributeError here, or something else?

        dest,size = thing
        self.Fields_clock.set_bits(dest,size, Bits(size, val))



if __name__ == "__main__":
    model = HWCSim(sys.stdin)
    model.dump()

    clock = model.run()

    print(clock.bits)
    print(clock.bits.asdf)
    print(clock.bits.foo.bar.baz)

