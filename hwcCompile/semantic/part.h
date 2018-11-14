#ifndef __SEMANTIC_PART_H__INCLUDED__
#define __SEMANTIC_PART_H__INCLUDED__


#include "names.h"
#include "stmt.h"


typedef HWC_Part     HWC_Part;
struct HWC_Part
{
	/* these track the progress of the semantic phase.  The 'completed'
	 * field tells us which semantic phase is done for this type; calling
	 * a generator function on this type, for one of these phases, is a
	 * NOP.  The 'begun' field tells you what phases have begun, which is
	 * used to detect recursive types.
	 */
	int phases_completed;
	int phases_begun;



	HWC_NameScope * publicNames;
	HWC_NameScope *privateNames;

	HWC_Stmt *stmts;
	int       stmts_len;

	HWC_Decl *decls;
	int       decls_len;

	// TODO: Field for sizeof Part
};


#endif

