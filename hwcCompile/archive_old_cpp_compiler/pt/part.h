#ifndef __PARSE_TREE__PART_H__INCLUDED__
#define __PARSE_TREE__PART_H__INCLUDED__


#include "wiring/fileRange.h"


typedef struct PT_part_decl PT_part_decl;

typedef struct PT_stmt PT_stmt;
typedef struct PT_type PT_type;
typedef struct PT_expr PT_expr;


struct PT_part_decl
{
	FileRange fr;

	char *name;

	// linked list, in reverse order of declaration
	PT_stmt *stmts;
};


// Debug functions

void dump_pt_part_decl (PT_part_decl  *obj, int spaces);


#endif
