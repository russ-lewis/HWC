#ifndef __SIM_TICK_H__INCLUDED__
#define __SIM_TICK_H__INCLUDED__


#include "sim/state.h"



/* this performs a complete tick, and then prints out any memory changes.
 */
void HWC_Sim_doTick(HWC_Sim_State*,
                    int (*write_callback)(HWC_Sim_State*,int,int),
                    int (*mem_update_callback)(HWC_Sim_State*,HWC_Wiring_Memory*));



/* these functions allow you to iterate through the steps of a tick one at
 * a time, so that the student can simulate what happens at each moment.
 */

/* do the init work at the start of a tick.  Wipe the entire bit space, and
 * then deliver the memory values to their respective 'read' sides.
 *
 * The memory values, as they are written to the bit space, will cause other
 * components to be posted to the TODO list - but none of those will be
  dispatched.
 */
void HWC_Sim_tick_init(HWC_Sim_State*);

/* query functions: are there any pending components on the TODO or deferred
 * lists?
 */
int HWC_Sim_tick_hasTODO(HWC_Sim_State*);
int HWC_Sim_tick_hasDeferred(HWC_Sim_State*);

/* dispatch up to 'count' values from the TODO list.  -1 means unlimited.
 * This will *never* dispatch from the deferred list.  It returns the number
 * of dispatch steps.  It also includes a callback, which (if not NULL) will
 * be called any time that any value is posted to the bit space.
 *
 * If the callback returns nonzero, then the dispatch process will terminate
 * and return immediately.  If it returns zero, then the process will continue
 * (or not) based on 'count' and the current contents of the TODO list.
 */
int HWC_Sim_tick_dispatchSome(HWC_Sim_State*,
                              int count,
                              int (*callback)(HWC_Sim_State*, int pos, int len));

/* same as previous, but will only dispatch from the deferred list.  Will
 * return immediately (returning 0) if there are any elements on the TODO list.
 * Since deferred operations almost always end up posting to the bit space (and
 * thus putting other elements on the TODO list), this will *always* terminate
 * after the first dispatch.  It returns 0 or 1 to indicate whether or not it
 * dispatched anything.
 */
int HWC_Sim_tick_dispatchDeferred(HWC_Sim_State*,
                                  int (*callback)(HWC_Sim_State*, int,int));

/* must not be called unless TODO and deferred are both empty.  Returns a
 * count of the number of bits of memory modified.  Includes a callback to be
 * called for each memory cell that is updated.
 */
int HWC_Sim_tick_finish(HWC_Sim_State*,
                        int (*callback)(HWC_Sim_State*, HWC_Wiring_Memory*));



/* THESE NEXT ONES NOT YET IMPLEMENTED */

/* duplicate the Sim State, so that you can go back in time (to a previous
 * tick, or earlier in the current tick), if desired.  If 'withinTick' is 1,
 * then we assume that this is saving state *within* the current tick; the
 * bit space will be duplicated, but the memory backing store will *not*.
 *
 * But if 'withinTick' is 0, then we will perform the same actions, but
 * additionally duplicate the memory backing store, so that we can track how
 * the memory changes over time.
 *
 * In BOTH CASES, the duplicate will have an *EMPTY* TODO and deferred lists,
 * because we don't allow you to perform any additional dispatches on the
 * duplicate.  The duplicate is for archiving old state *ONLY*.
 */
HWC_Sim_State *HWC_Sim_dup(HWC_Sim_State*, int withinTick);

void HWC_Sim_freeDup(HWC_Sim_State*);



#endif
