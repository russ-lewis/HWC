#ifndef __SIM_BIT_H__INCLUDED__
#define __SIM_BIT_H__INCLUDED__


/* Simulator: Individual Bits
 *
 * In the HWC simulator, each bit is tracked individually, even if it is part
 * of a large array.  Each bit has several possible states.
 *
 * The first three states are obvious:
 *    0 - the bit is literally false
 *    1 - the bit is literally true
 *    BIT_FLOATING - the bit is not yet connected to anything (init state)
 *
 * In the future, we plan to add:
 *    BIT_UNDEFINED - (see spec)
 *
 * However, the simulator also needs a special state, which is not obvious
 * from a cursory reading of the spec:
 *    BIT_FLOATING_CONNECTED
 * For the most part, this is treated like BIT_FLOATING (and it will generally
 * generally be reported to the user that way).  However, this state means
 * something different to the simulator: it means that the bit is on the
 * left-hand-side of a connection statement (either an unconditional one, or
 * a conditional one where the condition has resolved to TRUE).
 *
 * This allows us to detect several different errors, which might arise.
 * First, no bit can be on the left-hand-side of *TWO* connections, so if
 * you find a future connection into this, while already in the CONNECTED
 * state, then we have an error.  Second, if we have a connection to a
 * memory cell or flag, which moves to the CONNECTED state and stays there
 * forever, then it is an error which we can report at the *END* of the clock
 * cycle.  (Flags can only be connected to 1, if they are connected at all,
 * and memory cells can never have "floating" written to them.)
 */

enum HWC_bit_values
{
	BIT_FLOATING           = -1,
	BIT_FLOATING_CONNECTED = -2,
	BIT_UNDEFINED          = -1024,
};


static inline bit_isFloating(int b)
{
	return (b == BIT_FLOATING) || (b == BIT_FLOATING_CONNECTED);
}



#endif

