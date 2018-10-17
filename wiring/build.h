#ifndef __WIRING_BUILD_H__INCLUDED__
#define __WIRING_BUILD_H__INCLUDED__


/* WIRING (BUILD)
 *
 * This declares the types and functions necessary for main() to initiate
 * building the wiring diagram.  This is the external interface only.
 */


typedef struct HWC_Part   HWC_Part;
typedef struct HWC_Wiring HWC_Wiring;

HWC_Wiring *buildWiringDiagram(HWC_Part *part);


#endif

