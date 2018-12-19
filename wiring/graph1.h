#ifndef __WIRING_GRAPH1_H__INCLUDED__
#define __WIRING_GRAPH1_H__INCLUDED__

/* SEE ALSO: sim/graph2.h
 *
 * We have two different 'graph' types.  The first represents a graph in the
 * classic sense: it is made up (more or less) of just nodes and edges.  The
 * nodes represent various components in the wiring diagram; the edges
 * represent the depedencies between them (where an output writes to an
 * input).  This graph is defined implicitly, however; instead of having an
 * explicit edge list for each node, we instead have an *implicit* edge list
 * using the OverlapList type.
 *
 * The other graph type is used for the simulation.  It represents 
 */

TODO: rewrite: we only have a *SINGLE* graph type!  The OverlapList is the key!  The OverlapList makes the graph work; the header over in the sim/ directory should be renamed to "sim state", or something along those lines!



#include "wiring/overlapList.h"



#endif

