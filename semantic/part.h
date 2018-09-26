#ifndef __SEMANTIC_PART_H__INCLUDED__
#define __SEMANTIC_PART_H__INCLUDED__


#include "names.h"
#include "stmt.h"


typedef HWC_Part     HWC_Part;
struct HWC_Part
{
	HWC_NameScope *names;

	HWC_Stmt *stmts;
	int       stmts_len;
};


#endif

