#ifndef __WIRING_CORE_H__INCLUDED__
#define __WIRING_CORE_H__INCLUDED__


/* all valid index values are non-negative.  But we find it handy to have
 * a few special values, which represent unusual situations.
 */
enum {
	// represents "no such bit", such as the 'b' input for a NOT gate
	WIRING_BIT_INVALID = -1,

	// represents a constant 0 (printed as ZERO in the wiring diagram),
	// which is an arbitrary-size compile-time constant.
	WIRING_CONST_ZERO = -1000,
};


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
 *    HWC_Wiring_Memory - represents a range of memory cells.  Gives the size
 *                        and bit-index of both the read and write elements.
 *
 *    HWC_Wiring_Logic - represents a single logical operator.  Can handle
 *                       range inputs.  Gives the bit-index of the start of the
 *                       input and output field(s).
 *
 *    HWC_Wiring_Connection - represents a connection.  Can handle range
 *                            connections.  Gives the in and out locations.  If
 *                            conditional, gives the (single) bit which
 *                            controls the condition.  If undirected, has a
 *                            flag to indicate that.
 *
 *    HWC_Wiring_Assert - represents an assertion.
 *
 * NOTE: You will observe that the types listed only have enough information
 *       to read/write the wiring diagram file.  It does *NOT* include any
 *       dynamic information.  Instead, the Sim struct family will have all
 *       of that - and each Sim object will have pointers to help find the
 *       matching design elements in the Wiring.
 */


typedef struct HWC_Wiring            HWC_Wiring;
typedef struct HWC_Wiring_Memory     HWC_Wiring_Memory;
typedef struct HWC_Wiring_Logic      HWC_Wiring_Logic;
typedef struct HWC_Wiring_Connection HWC_Wiring_Connection;
typedef struct HWC_Wiring_Assert     HWC_Wiring_Assert;

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

	/* an array of HWC_Wiring_Memory objects.  Each object represents a
	 * single contiguous range of memory cells; there are bit-indices for
	 * both the read and write sides.
	 */
	int numMemRanges;
	HWC_Wiring_Memory *mem;

	/* an array of HWC_Wiring_Logic objects.  Each object represents a
	 * single logical operator, which can be over a single bit or over
	 * many bits.
	 */
	int numLogicalOperators;
	HWC_Wiring_Logic *logic;

	/* an array of HWC_Wiring_Connection objects.  Each object represents a
	 * single connection, which might be over a single bit, or a range of
	 * them.  Handles conditional and undirected connections as well.
	 */
	int numConnections;
	HWC_Wiring_Connection *conns;

	/* an array of HWC_Wiring_Assert objects.  Each object represents a
	 * single assertion, which always reads a single bit.
	 */
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


#endif

