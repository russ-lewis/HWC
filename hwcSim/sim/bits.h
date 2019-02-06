#ifndef __SIM_BITS_H__INCLUDED__
#define __SIM_BITS_H__INCLUDED__


#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "wiring/core.h"
#include "sim/runtime_errors.h"



/* BIT STORAGE
 *
 * For the bits, we want to store complex state (more than just 0/1), but we
 * don't want to pay the runtime cost of having large, heavyweight types for
 * each of them (especially since we expect large blocks of bits to be
 * treated as busses, and thus have the same state at all times).
 *
 * For most of the simulator's runtime, there are really only three states
 * that we might care about.  So we will allocate exactly *two* bits of real
 * storage, with three defined values and one reserved value.  The four
 * values are:
 *     00 - FLOATING - the bit is not set yet
 *     10 - SET_0    - the bit has been set to 0
 *     11 - SET_1    - the bit has been set to 1
 *     01 - RESERVED - not currently used.  In the future, will require a
 *                     lookup in a more complex data structure.
 */



static inline char *HWC_Sim_bitsAlloc(int numBits)
{
	// round up
	int numBytes = (numBits+3)/4;

printf("FIXME: %s(): Convert to using mmap()\n", __func__);
	return calloc(numBytes,1);
}



static inline int bit_get_state(char *buf, int indx)
{
	// there are 4 states per byte.  bit[0] in the space is the low-order
	// two bits of the first byte.

	return (buf[indx/4] >> (2*(indx%4))) & 0x3;
}



static inline int bit_is_floating(char *buf, int indx)
{
	return bit_get_state(buf, indx) == 0;
}

static inline int bit_is_set(char *buf, int indx)
{
	int state = bit_get_state(buf,indx);
	return state == 2 || state == 3;
}

static inline int bit_range_is_set(char *buf, int indx,int len)
{
	assert(len > 0);

	int i;
	for (i=0; i<len; i++)
		if (bit_is_set(buf, indx+i) == 0)
			return 0;
	return 1;
}



static inline void bit_set(char *buf, int indx, int val)
{
	assert(val == 0 || val == 1);
	int state = 2+val;

	if (bit_get_state(buf,indx) != 0)
	{
		HWC_Sim_reportShortCircuit(indx);
		return;
	}

	buf[indx/4] |= (state << (2*(indx%4)));
}

static inline void bit_set_range(char *buf, int indx,int len, unsigned long val)
{
	assert(len > 0 && len < 8*sizeof(val));

	assert((val >> len) == 0);

	int i;
	for (i=0; i<len; i++)
		bit_set(buf, indx+i, (val >> i) & 0x1);
}



static inline int HWC_Sim_calcNumMemBits(HWC_Wiring *wiring)
{
	int retval = 0;

	int i;
	for (i=0; i<wiring->numMemRanges; i++)
		retval += wiring->mem[i].size;

	return retval;
}

static inline char *HWC_Sim_memBitsAlloc(int numBits)
{
	// round up
	int numBytes = (numBits+7)/8;

	// NOTE: All memory cells start as 0
	return calloc(numBytes,1);
}



#endif

