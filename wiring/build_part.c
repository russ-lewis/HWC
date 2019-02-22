#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "wiring/build.h"
#include "wiring/core.h"
#include "../hwcCompile/semantic/part.h"
#include "../hwcCompile/semantic/decl.h"


// Prototypes, used later
int findMemory (HWC_Wiring *, HWC_Part *, int);
int findLogic  (HWC_Wiring *, HWC_Part *, int);
int findConnect(HWC_Wiring *, HWC_Part *, int);
int findAssert (HWC_Wiring *, HWC_Part *, int);


HWC_Wiring *buildWiringDiagram(HWC_Part *part)
{
	HWC_Wiring *retval = malloc(sizeof(HWC_Wiring));

	// Size
	retval->numBits = part->size;

	// Memory
	retval->numMemRanges = part->numMemory;
	retval->mem = malloc(sizeof(HWC_Wiring_Memory) * part->numMemory);
	int memFound = findMemory(retval, part, 0);
	if(memFound != part->numMemory)
		assert(0);

	// Logic

	// Connections

	// Asserts

	assert(0);
}

int findMemory(HWC_Wiring *retval, HWC_Part *part, int index)
{
	int i;
	HWC_Decl currDecl;
	for(i = 0; i < part->decls_len; i++)
	{
		currDecl = part->decls[i];

		if(currDecl.base_part != NULL)
			index = findMemory(retval, currDecl.base_part, index);

		if(currDecl.isMem == 1)
		{
			HWC_Wiring_Memory currMem = retval->mem[index];
			currMem.size = currDecl.indexSize;
			// TODO: What to put for these?
			currMem.read = -1;
			currMem.write = -1;
		}
	}
	return index;
}

int findLogic(HWC_Wiring *retval, HWC_Part *part, int index)
{
	return index;
}
int findConnect(HWC_Wiring *retval, HWC_Part *part, int index)
{
	return index;
}
int findAssert(HWC_Wiring *retval, HWC_Part *part, int index)
{
	return index;
}

/*
struct HWC_Wiring
{
	// how many bits are there in the entire system.  This is equal to the
	// size of the compiled 'main' part.  Of course, it includes bits for
	// all of the public plus, plus private plugs, plus all of the public
	// and private plugs of the many subcomponents - including implicit
	// plugs for every built-in logical component used in the entire
	// system.
	int numBits;

	// an array of HWC_Wiring_Memory objects.  Each object represents a
	// single contiguous range of memory cells; there are bit-indices for
	// both the read and write sides.
	int numMemRanges;
	HWC_Wiring_Memory *mem;

	// an array of HWC_Wiring_Logic objects.  Each object represents a
	// single logical operator, which can be over a single bit or over
	// many bits.
	int numLogicalOperators;
	HWC_Wiring_Logic *logic;

	// an array of HWC_Wiring_Connection objects.  Each object represents a
	// single connection, which might be over a single bit, or a range of
	// them.  Handles conditional and undirected connections as well.
	int numConnections;
	HWC_Wiring_Connection *conns;

	// an array of HWC_Wiring_Assert objects.  Each object represents a
	// single assertion, which always reads a single bit.
	int numAsserts;
	HWC_Wiring_Assert *asserts;
};


struct HWC_Wiring_Memory
{
	int size;     // how many bits?
	int read;     // index of 1st bit of the 'read' side
	int write;    // index of 1st bit of the 'write' side

	char *debug;
};


enum {
	WIRING_AND = 1,
	WIRING_OR,
	WIRING_XOR,
	WIRING_NOT,
	WIRING_EQ,
	WIRING_NEQ,
};
struct HWC_Wiring_Logic
{
	int type;     // use the enum above
	int size;
	int a,b;      // b is ignored for NOT, but used for all others
	int out;

	char *debug;
};


struct HWC_Wiring_Connection
{
	int size;     // how many bits?
	int to;       // index of 1st bit of the lhs of the assignment
	int from;     // index of 1st bit of the rhs of the assignment

	int condition;   // WIRING_BIT_INVALID if not conditional
	int isUndir;     // 1 if undirected; 0 if directed

	char *debug;
};


struct HWC_Wiring_Assert
{
	int bit;     // the bit to read

	char *debug;
};
*/
