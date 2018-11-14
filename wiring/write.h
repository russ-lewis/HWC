#ifndef __WIRING_WRITE_H__INCLUDED__
#define __WIRING_WRITE_H__INCLUDED__


/* WIRING (WRITE)
 *
 * This declares the function necessary for main() to write out a
 * wiring file.
 */


typedef struct HWC_Wiring HWC_Wiring;

int wiring_write(HWC_Wiring*, char *outfile);


#endif

