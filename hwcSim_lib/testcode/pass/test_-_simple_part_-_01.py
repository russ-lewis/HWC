#! /usr/bin/python3

import hwcSim

wires = hwcSim.HWCSim(open("simple_part.wires"))

state = wires.first_state()

for i in range(8):
    fields = state.fields
    fields.main.input = (i//2)%2
    state.run()
    print(f"input: {fields.main.input} output: {fields.main.output}")

    state = state.next()

