#ifndef __PARSE_TREE__PART_H__INCLUDED__
#define __PARSE_TREE__PART_H__INCLUDED__


typedef struct PT_part_decl PT_part_decl;
typedef struct PT_array_decl PT_array_decl;

typedef struct PT_stmt PT_stmt;
typedef struct PT_type PT_type;
typedef struct PT_expr PT_expr;


struct PT_part_decl
{
	char *name;

	// linked list, in reverse order of declaration
	PT_stmt *stmts;
};


struct PT_array_decl
{
	PT_array_decl *prev;

	PT_expr *size;
};


// Debug functions

void dump_part_decl (PT_part_decl  *obj, int spaces);
void dump_array_decl(PT_array_decl *obj, int spaces);


#endif
