There are three basic classifications of HWC-related programs (at least, three
that I can currently forsee):
  - Compiler
    Turns .hwc files into .wire files.

  - Simulator
    Reads .wire files, and runs multi-cycle simulations

  - Optimizers/Static Analysis Tools
    Read in .wire files, do analysis on the graph, and produces new .wire
    files with changed contents.

These tools share some, but not all, of the data structures:

  - .hwc Parse Tree
    Specific to the compiler, stored in hwcCompile/pt/

  - .hwc Semantic Tree and NameScope objects
    Specific to the compiler, stored in hwcCompile/semantic

  - Wire Diagram
    Used by all programs.  Generated from the semantic structures in the
    compiler, and then written out to a file.  Read from a file in the
    simulator.  Read from a file, edited, and then re-written by static
    analysis tools.

    Stored in wiring/

  - Graph
    Represents the relationships between various components, where components
    from the wiring diagram are nodes, and edges represent output/input links.
    That is, an edge from X to Y means that X writes to one or more bits which
    are read by Y.

    This data structure is used both by the simulator, and by static analysis
    tools.  Its contents are *static*, even in the simulator - meaning that
    these are the properties which do not change from cycle to cycle.

    Since this is static information, this does not contain any information
    that is not already present in the wiring diagram; however, it *encodes*
    that information in a form that makes it easier to use.

    Not all tools make use of all of the features of this system; for
    instance, the simulator uses the "forward" overlap table (looking to see
    which components need to be notified when a bit is written to), but it
    does *NOT* use the "backward" overlap table (seeing which components might
    write to a certain bit).

    Stored in graph/

  - Bit State
    Represents the current contents of the bits during a certain clock cycle.
    Only used by the simulator; this changes every clock cycle.

    This includes both the "bit space" (that is, the space of input/output
    bits which the various components read and write) and the "memory state
    space", a separate array, which stores the current state of all of the
    memory cells in the system.

    Stored in hwcSim/sim/

POINTERS, IMPLEMENTATION, AND RELATIONSHIPS

The parse tree does not know about any of the other data structures.

The semantic tree does not know about any of the other data structures; data
is copied out of the parse tree, and into the semantic tree.  (NOTE: This rule
could be flexed if necessary; it's OK if, in the future, the semantic tree
contained pointers into the parse tree.  I think it even less likely that the
sematic tree would ever contain pointers into the wiring diagram.)

The wiring diagram is a strict, one-to-one representation of the file.  It
does not contain any references to any other data structures.

The graph structures include pointers to the wiring structures.  Thus, the
graph structure can omit almost all of the information that is already present
in the wiring diagram; it includes this information by reference.
Conceptually, we don't think of the graph as containing any simulation
information; however, in practice it contains a few fields which are ignored
by static analysis tools but critical for simulation.

The simulation structures store the current state of the simulation, which
changes from cycle to cycle.  This is made up of the bits array (which stores
the contents of the bit space) and the memory state space (which stores the
contents of all of the memory cells, from cycle to cycle).  While there is a
single structure which represents all of the 'sim' data (with pointers to both
of the big buffers, as well into the graph data structure) some of the
critical fields associated with the 'sim' structures are actually declared
within the 'graph' data structures.  These include the double-linked list
pointers (for the TODO/pending lists) and the "partial write" metadata.

The reason that some of the 'sim' fields are stored within the 'graph' is
because the overlap table (which is a part of the 'graph') is a critical
component in the simulation; when we write to some bits, we need to "awaken"
any and all other components which might be reading those bits.  However, the
overlap table is made up of "component" objects which are part of the graph
data structure.  Instead of finding some weird "reverse lookup" which would
allow us to map the 'graph' components to 'sim' equivalents, we simply
locate per-component sim metadata in the 'graph' component; these fields are
ignored from the "graph" code, but critical from the "sim" code.

