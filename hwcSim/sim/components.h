

TODO: this will model the various components, but focus on their *simulation*
      state.  It will (probably) have links from each one to the Wiring Diagram
      version, which will contain the persistent information (while this will
      hold the dynamic information.

      It will almost certainly include a "base" object which implements common
      functionality; see below.


struct HWC_Sim_ComponentCore
{
	// the "TODO" and "deferred" lists are doubly-linked circular
	// lists (so that it's easy to remove them having nothing but a
	// pointer to the node).
	HWC_Sim_ComponentCore *prev, *next;


	// components can have up to 2 input ranges, and one output ranges.
	// Many component types have matching sizes for inputs/outputs and
	// the outputs themselves, but this is not universally true, so we
	// won't assume it.
	//
	// To mark any range as "not in use", set its starting point to -1.

	int in1_start, in2_start, out_start;   // inclusive
	int in1_end,   in2_end,   out_end;     // exclusive


	// this stores partial-write information.  To look at this, always
	// first check the integer, which can take on 2 magic values:
	//
	//    0 - this component has not posted *ANY* output, but might
	//        later.  This includes components which don't produce
	//        any bit output (such as assert) but which definitely
	//        need to read the inputs when they become available.
	//
	//   -1 - this compnent will *NOT* post any output in the future,
	//        either because it has actually written the values, or
	//        because it's a conditional connection, and it has
	//        decided not to write because the condition was false.
	//
	// If the integer is any *other* value, then it is interpreted as
	// information about a partial write, meaning that the component has
	// set *some* of the output bits but not all of them.  This is
	// interpreted in two ways, based on the size of the output:
	//
	//    If the output size is <= the number of bits in the integer,
	//    then the integer is used as a bitmask, with 1s indicating
	//    which bit(s) have been written so far.
	//
	//    Otherwise, the pointer is used, and it is a pointer to a
	//    malloc()ed buffer, which contains the bitmask.

	union {
		long  l;
		char *buf;
	} partialWrite;
};


