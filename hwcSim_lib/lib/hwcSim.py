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

        self.conns       = []
        self.cond_conns  = []
        self.const_conns = []    # for x=1 connections
        self.logic       = []
        self.memory      = []

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

        def watch_callback(data):
            assert type(data) == Bits, data

            if data.mask is not None:
                TODO()

            nonlocal delivered
            if delivered:
                return
            delivered = True

            rec = HistoryRecord(self.  to_bit, self.  to_bit+self.size,
                               (self.from_bit, self.from_bit+self.size),
                               None)
            cycle.set_bits(self.to_bit, self.size, data, rec)

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

        self.fields    = Fields(self, self.wiring.names)
        self.bit_space = BitSpaceNode(0, self.wiring.bit_count)

        # this tracks the "history" of sets that have happened in the space,
        # this clock cycle.  Each record is a range that has been set, along
        # with the dependencies (if any) which were required to be known before
        # this happened.
        #
        # The primary purpose of this is as a reporting tool, so that users can
        # visualize the action in a GUI (and perhaps run the evaluations
        # out-of-order).  But a critical secondary purpose is that, by keeping
        # an index into this array, we have a TODO marker which tells us which
        # watches need to be alerted about recent changes.
        self.history = []

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

        for c in self.wiring.const_conns:
            dest = c.to_bit
            size = c.size
            val  = Bits(size, c.val)
            hist = HistoryRecord(dest,size, "const",None)
            self.set_bits(dest,size, val, hist)

    def set_bits(self, start,size, val, history):
        assert val.mask is None
        assert val.val >> size == 0

        assert type(history) == HistoryRecord

        self.history.append(history)
        self.bit_space.set_bits(start, start+size, val)

    def find_indx_for_range(self, dest,size, split=True):
        assert dest+size <= self.wiring.bit_count

        if split:
            retval = self.bit_space.split_at(dest)
            self.bit_space.split_at(dest+size)

        return retval

    def get_bits(self, start,size):
        return self.bit_space.get_bits(start, start+size)

    def add_watch(self, dest,size, callback):
        self.bit_space.add_watch(dest, dest+size, callback)

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
        # when we begin, the user inputs (if any), memory (if any), and
        # const connections (if any) have all delivered their values to the
        # various bits.  Each of those operations should have set up a matching
        # HistoryRecord.  We will use these as the TODO items for our search
        # for watches to call; we loop until we have delivered all of the
        # watch callbacks, with no new ones appearing.
        #
        # In addition to the "complete" watch callbacks, we also need to
        # sometimes deliver "partial" ones (that is, ones where only part of
        # the range is known yet); we procrastinate on these as long as
        # possible (always preferring to give complete ones), but if we
        # exhaust all of the complete callbacks, we will use the partials
        # in hopes of forcing some last-minute updates.
        #
        # while there_are_pending_complete_or_partial_callbacks:
        #     if there_are_complete_callbacks_pending:
        #         flush_until_none
        #     else:
        #         perform_a_single_partial_callback
        #
        # A final note on the callbacks: all callbacks have 3 required
        # arguments:
        #     cur_clock
        #     start
        #     end
        # and one optional argument:
        #     force=False
        #
        # We use the same callback for both complete and partial callbacks;
        # we send a partial callback (if appropriate) by setting Force=True,
        # which tells the component to set its outputs using masks if possible.

        # these two are indices into the history[] array, which tell us how
        # much of the history we've flushed so far.  The partial is always <=
        # the complete
        complete_pos = 0
        partial_pos  = 0

        while partial_pos < len(self.history):
            if complete_pos < len(self.history):
                while complete_pos < len(self.history):   # history can be added as we go
                    rec = self.history[complete_pos]
                    complete_pos += 1
                    self.bit_space.send_callbacks(rec.start, rec.end)

            else:
                assert partial_pos < complete_pos
                rec = self.history[partial_pos]
                partial_pos += 1
                self.bit_space.send_callbacks(rec.start, rec.end, partials=True)



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

            retval = self.Fields_clock.get_bits(start,size)

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
        self.Fields_clock.set_bits(dest,size, Bits(size, val),
                                   HistoryRecord(dest, dest+size, "user",None))



class BitSpaceNode:
    def __init__(self, start,end, val=None, watches=[]):
        self.start   = start
        self.end     = end
        self.watches = watches

        # all nodes start out as leaf nodes.  Leaf nodes have 'val' fields,
        # which start as None but might be set to Bits objects if there are
        # set_bits() calls that go down the tree.
        #
        # But when we split the node, we create left and right children, and
        # the node no longer has a val.  (We mark this by replacing the val
        # with the string "not leaf".)  Instead, portions of the val (if not
        # None) are sent down into the new leaves.
        #
        # 9Note that this tree is *NOT* guaranteed to be balanced, but that we
        # never have single-child nodes, either.)
        #
        # Both leaf nodes and internal nodes can have watch callbacks assigned;
        # at all times, each watch callback is registered only once, at the
        # lowest node that contains the *entire* range.  (Worst case, we might
        # have watch callbacks on the root!)

        self.val = None

    def is_leaf(self):
        return self.val != "not leaf"

    def split_at(self, pos):
        # check for NOPs
        if pos == self.start or pos == self.end:
            return

        # never re-split an internal node
        if not self.is_leaf():
            if pos < self.splitAt:
                self.lft.split_at(pos)
            else:
                self.rgt.split_at(pos)
            return

        # this is a leaf node.  Split it!

        # watches can go left,right, or stay in the current node.
        w_lft = [(s,e,w) for s,e,w in self.watches if e <= pos]
        w_rgt = [(s,e,w) for s,e,w in self.watches if s >= pos]
        w_me  = [(s,e,w) for s,e,w in self.watches if s < pos and e > pos]
        assert len(w_lft) + len(w_rgt) +len(w_me) == len(self.watches)
        self.watches = w_me

        # split the value (if any)
        if self.val is None:
            v_lft = None
            v_rgt = None
        else:
            v_lft,v_rgt = self.val.split(pos-self.start)

        self.val     = "not leaf"
        self.splitAt = pos;
        self.lft     = BitSpaceNode(self.start,pos,          v_lft, w_lft)
        self.rgt     = BitSpaceNode(           pos,self.end, v_rgt, w_rgt)

    def dump(self, prefix):
        if self.is_leaf():
            print(f"{prefix}{self.start} {self.end} - VAL {self.val} - WATCHES {len(self.watches)}")
        else:
            print(f"{prefix}{self.start} {self.end} - SPLIT AT {self.splitAt} - WATCHES {len(self.watches)}")
            print(f"{prefix}  lft:")
            self.lft.dump(prefix+"    ")
            print(f"{prefix}  rgt:")
            self.rgt.dump(prefix+"    ")

    def add_watch(self, start,end, callback):
        assert start < end
        assert callback is not None
        assert start >= self.start
        assert end   <= self.end

        if self.is_leaf() or start < self.splitAt and end > self.splitAt:
            self.watches.append( (start,end,callback) )
        else:
            if end <= self.splitAt:
                self.lft.add_watch(start,end, callback)
            else:
                self.rgt.add_watch(start,end, callback)

    def set_bits(self, start,end, val):
        assert start >= self.start
        assert end   <= self.end

        assert start < end, (start,end)

        assert val.mask is None    # TOOD: later, support masked sets
        assert val.val >> (end-start) == 0

        # happiest case: exact match on a leaf.
        if self.is_leaf() and start == self.start and end == self.end:
            assert val.mask is None    # TODO: handle partial writes, later!

            if self.val is not None:
                raise HWCRuntime_MultipleConnectionError()
            self.val = val
            return

        # if the current node is a leaf, then it must be the wrong shape.
        # Split it up.
        if self.is_leaf():
            self.split_at(start)
            self.split_at(end)
            assert not self.is_leaf()

        # single-child recursion
        if not self.is_leaf() and end <= self.splitAt:
            self.lft.set_bits(start,end, val)
            return
        if not self.is_leaf() and self.splitAt <= start:
            self.rgt.set_bits(start,end, val)
            return

        # recursion into both children (including the special case where a
        # node that was recently a leaf was split)

        assert start < self.splitAt
        assert         self.splitAt < end

        val_l,val_r = val.split_at(self.split_at-start)
        if val_l is not None:
            self.lft.set_bits(start, self.splitAt,      val_l)
        if val-r is not None:
            self.rgt.set_bits(       self.splitAt, end, val_r)

    def get_bits(self, start,end):
        assert start >= 0
        assert end   >  start

        if self.is_leaf():
            if self.start == start and self.end == end:
                assert type(self.val) == Bits, self.val
                assert self.val.mask is None
                return self.val
            else:
                TODO()    # handle reads which are subsets of a leaf

        # not leaf
        if end <= self.splitAt:
            return self.lft.get_bits(start,end);
        if self.splitAt <= start:
            return self.rgt.get_bits(start,end);

        TODO()    # handle reads which span multiple leaves

    def send_callbacks(self, start,end, partials=False):
        assert start >= self.start
        assert end   <= self.end

        for s,e,w in self.watches:
            if e <= start or s >= end:
                continue    # no overlap whatsoever
            if not partials and (s < start or e >end):
                continue    # insufficient overlap if we're not doing partial

            data = self.get_bits(start,end)
            assert type(data) == Bits, data
            w(data)

        if not self.is_leaf():
            if end <= self.splitAt:
                self.lft.send_callbacks(start,end, partials)
            if self.splitAt <= start:
                self.rgt.send_callbacks(start,end, partials)
            if start < self.splitAt and self.splitAt < end:
                self.lft.send_callbacks(start,self.splitAt,     partials)
                self.rgt.send_callbacks(      self.splitAt,end, partials)



class HistoryRecord:
    def __init__(self, start,end, cause1, cause2):
        self.start  = start
        self.end    = end
        self.cause1 = cause1
        self.cause2 = cause2



if __name__ == "__main__":
    model = HWCSim(sys.stdin)
    model.dump()

    clock = model.run()

    print(clock.bits)
    print(clock.bits.asdf)
    print(clock.bits.foo.bar.baz)

