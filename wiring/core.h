#ifndef __WIRING_CORE_H__INCLUDED__
#define __WIRING_CORE_H__INCLUDED__


/* WIRING (CORE)
 *
 * This declares the HWC_Wiring struct, and the various subtypes used by it:
 *
 *    HWC_Wiring - the unified struct, which represents an entire wiring
 *                 diagram.  It defines the number of bits in the system, the
 *                 number of logical operators, and the number of
 *                 unconditional and condition connections.  Has a list of
 *                 bit ranges which are flags.
 *
 *    HWC_WiringMemory - represents a range of memory cells.  Gives the size
 *                       and bit-index of both the read and write elements.
 *
 *    HWC_WiringLogic - represents a single logical operator.  Can handle
 *                      range inputs.  Gives the bit-index of the start of the
 *                      input and output field(s).
 *
 *    HWC_WiringConnection - represents an unconditional connection.  Can
 *                     handle range connections.  Gives the in and out
 *                     locations.  If conditional, gives the (single) bit
 *                     which controls the condition.  If undirected, has a
 *                     flag to indicate that.
 *
 * NOTE: You will observe that the types listed only have enough information
 *       to read/write the wiring diagram file.  It does *NOT* include any
 *       dynamic information.  Instead, the Sim struct family will have all
 *       of that - and each Sim object will have pointers to help find the
 *       matching design elements in the Wiring.
 */


typedef struct HWC_Wiring           HWC_Wiring;
typedef struct HWC_WiringMemory     HWC_WiringMemory;
typedef struct HWC_WiringLogic      HWC_WiringLogic;
typedef struct HWC_WiringConnection HWC_WiringConnection;

struct HWC_Wiring
{
	/* how many bits are there in the entire system.  This is equal to the
	 * size of the compiled 'main' part.  Of course, it includes bits for
	 * all of the public plus, plus private plugs, plus all of the public
	 * and private plugs of the many subcomponents - including implicit
	 * plugs for every built-in logical component used in the entire
	 * system.
	 */
	int numBits;

	/* an array of HWC_WiringMemory objects.  Each object represents a
	 * single contiguous range of memory cells; there are bit-indices for
	 * both the read and write sides.
	 */
	int numMemRanges;
	HWC_WiringMemory *mem;

	/* an array of HWC_WiringLogic objects.  Each object represents a
	 * single logical operator, which can be over a single bit or over
	 * many bits.
	 */
	int numLogicalOperators;
	HWC_WiringLogic *logic;

	/* an array of HWC_WiringConnection objects.  Each object represents a
	 * single connection, which might be over a single bit, or a range of
	 * them.  Handles conditional and undirected connections as well.
	 */
	int numConnections;
	HWC_WiringConnection *conns;
};


struct HWC_WiringMemory
{
	int size;     // how many bits?
	int read;     // index of 1st bit of the 'read' side
	int write;    // index of 1st bit of the 'write' side
};


struct HWC_WiringLogic
{
};


struct HWC_WiringConnection
{
};


#endif

