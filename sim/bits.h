#ifndef __SIM_BITS_H__INCLUDED__
#define __SIM_BITS_H__INCLUDED__


#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <assert.h>

#include "wiring/core.h"
#include "sim/runtime_errors.h"
#include "sim/notify.h"
#include "graph/overlapTable.h"



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

	// TODO: I'd like to allocate using mmap().  But while that works
	//       just fine for this call, it doesn't work for the next
	//       function (bitsWipe()) because (as far as I can tell)
	//       MAP_FIXED doesn't work under Cygwin.
#if 0
	// round up to number of pages
	int pageSz = getpagesize();
	int pageBytes = (numBytes+pageSz-1) & ~(pageSz-1);

	char *retval = mmap(NULL,
	                    pageBytes,
	                    PROT_READ | PROT_WRITE,
	                    MAP_ANONYMOUS | MAP_PRIVATE,
	                    0,0);

	if (retval == MAP_FAILED)
		return NULL;
	else
		return retval;
#endif

	return calloc(numBytes,1);
}

static inline void HWC_Sim_bitsWipe(char *buf, int numBits)
{
	// round up
	int numBytes = (numBits+3)/4;

#if 0
	int pageSz = getpagesize();
	int pageBytes = (numBytes+pageSz-1) & ~(pageSz-1);

	// almost the same as bitsAlloc...but re-allocating in place
	char *retval = mmap(buf,
	                    pageBytes,
	                    PROT_READ | PROT_WRITE,
	                    MAP_ANONYMOUS | MAP_PRIVATE | MAP_FIXED,
	                    0,0);

	// theoretically, that mmap() call can fail.  In practice, it
	// won't.  I guess.  So I'll hack in an assert() to enforce my
	// only partially-justifiable assumption.
	assert(retval == buf);
#endif

	memset(buf, 0, numBytes);
}



static inline int HWC_Sim_bit_getState(char *buf, int indx)
{
	// there are 4 states per byte.  bit[0] in the space is the low-order
	// two bits of the first byte.

	return (buf[indx/4] >> (2*(indx%4))) & 0x3;
}



static inline int HWC_Sim_bit_isFloating(char *buf, int indx)
{
	return HWC_Sim_bit_getState(buf, indx) == 0;
}

static inline int HWC_Sim_bit_isValid(char *buf, int indx)
{
	int state = HWC_Sim_bit_getState(buf,indx);
	return state == 2 || state == 3;
}

static inline int HWC_Sim_bit_rangeIsValid(char *buf, int indx,int len)
{
	assert(len > 0);

	int i;
	for (i=0; i<len; i++)
		if (HWC_Sim_bit_isValid(buf, indx+i) == 0)
			return 0;
	return 1;
}



static inline int HWC_Sim_readBit(char *buf, int indx)
{
	int state = HWC_Sim_bit_getState(buf,indx);
	assert((state & 0x2) == 2);   // valid bit must be set!

	return state & 0x1;
}

static inline void HWC_Sim_writeBit(char *buf, int indx, int val,
                                    HWC_Graph_OverlapRange *notify)
{
	assert(val == 0 || val == 1);
	int state = 2+val;

	if (HWC_Sim_bit_getState(buf,indx) != 0)
	{
		HWC_Sim_reportShortCircuit(indx);
		return;
	}

	buf[indx/4] |= (state << (2*(indx%4)));

	if (notify != NULL)
		HWC_Sim_notify(notify, indx,1);
}

static inline unsigned long HWC_Sim_readBitRange(char *buf, int indx,int len)
{
	assert(len <= 8*sizeof(unsigned long));
	unsigned long retval = 0;

	int i;
	for (i=0; i<len; i++)
	{
		int bit = HWC_Sim_readBit(buf, indx+i);
		retval |= (bit << i);
	}

	return retval;
}

static inline void HWC_Sim_writeBitRange(char *buf, int indx,int len, unsigned long val,
                                         HWC_Graph_OverlapRange *notify)
{
	assert(len > 0 && len < 8*sizeof(val));
	assert((val >> len) == 0);

	int i;
	for (i=0; i<len; i++)
		HWC_Sim_writeBit(buf, indx+i, (val >> i) & 0x1, NULL);

	if (notify != NULL)
		HWC_Sim_notify(notify, indx,len);
}

static inline void HWC_Sim_copyBitRange(char *buf, int dst,int src, int len,
                                        HWC_Graph_OverlapRange *notify)
{
	assert(len > 0);

	int i;
	for (i=0; i<len; i++)
	{
		int val = HWC_Sim_readBit(buf, src+i);
		HWC_Sim_writeBit(buf, dst+i, val, NULL);
	}

	if (notify != NULL)
		HWC_Sim_notify(notify, dst,len);
}



static inline void HWC_Sim_writeRawBit(char *buf, int indx, int val)
{
	assert(val == 0 || val == 1);

	int byte =        indx/8;
	int mask = (1 << (indx%8));

	if (val == 0)
		buf[byte] &= ~mask;
	else
		buf[byte] |=  mask;
}

static inline void HWC_Sim_writeRawBitRange(char *buf, int indx,int len, unsigned long val)
{
	assert(len > 0 && len < 8*sizeof(val));
	assert((val >> len) == 0);

	int i;
	for (i=0; i<len; i++)
		HWC_Sim_writeRawBit(buf, indx+i, (val >> i) & 0x1);
}

static inline int HWC_Sim_readRawBit(char *buf, int indx)
{
	int rawByte = indx/8;
	int rawBit  = indx%8;
	return (buf[rawByte] >> rawBit) & 0x1;
}

static inline unsigned long HWC_Sim_readRawBitRange(char *buf, int indx,int len)
{
	unsigned long retval = 0;
	assert(len <= 8*sizeof(retval));

	int i;
	for (i=0; i<len; i++)
		retval |= (HWC_Sim_readRawBit(buf,indx+i) << i);

	return retval;
}



static inline int *HWC_Sim_buildMemOffsets(HWC_Wiring *wiring)
{
	assert(wiring->numMemRanges > 0);

	int *retval = malloc((wiring->numMemRanges+1) * sizeof(int));
	if (retval == NULL)
		return NULL;

	int cur = 0;
	int i;
	for (i=0; i<wiring->numMemRanges; i++)
	{
		retval[i] = cur;
		cur += wiring->mem[i].size;
	}

	// this is never used, except to figure out the length of the
	// total memory set.
	retval[wiring->numMemRanges] = cur;

	return retval;
}

static inline char *HWC_Sim_memBitsAlloc(int numBits)
{
	// round up
	int numBytes = (numBits+7)/8;

	// NOTE: All memory cells start as 0
	return calloc(numBytes,1);
}



static inline void HWC_Sim_copyRawToBitSpace(char *bitSpaceBuf,
                                             int bitSpacePos, int size,
                                             char *rawBuf,
                                             int rawPos,
                                             HWC_Graph_OverlapRange *notify)
{
	// TODO: make more efficient by reading/writing multiple bits at
	//       once.  But, since there's no reason to assume that the
	//       ranges have any association at all in how they're aligned,
	//       any block strategy we choose will probably be misalgned
	//       in one or the other system.  (sigh)

	int i;
	for (i=0; i<size; i++)
	{
		int val = HWC_Sim_readRawBit(rawBuf, rawPos+i);
		HWC_Sim_writeBit(bitSpaceBuf, bitSpacePos+i, val, NULL);
	}

	if (notify != NULL)
		HWC_Sim_notify(notify, bitSpacePos,size);
}



#endif

