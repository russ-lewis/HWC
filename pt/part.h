#ifndef __PARSE_TREE__PART_H__INCLUDED__
#define __PARSE_TREE__PART_H__INCLUDED__

#include "debug.h"

typedef struct PT_part_decl PT_part_decl;
typedef struct PT_part_stmt PT_part_stmt;

typedef struct PT_type PT_type;
typedef struct PT_expr PT_expr;

typedef struct PT_array_decl PT_array_decl;


struct PT_part_decl
{
	char *name;

	/* linked list, in reverse order of declaration */
	PT_part_stmt *stmts;
};

struct PT_part_stmt
{
	/* linked list, in reverse order of declaration */
	PT_part_stmt *prev;

	PT_type *type;
	char        *name;
};


struct PT_array_decl
{
	PT_array_decl *prev;

	PT_expr *size;
};

// Debug functions

static void dump_part_decl(PT_part_decl *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("Part_decl: named '%s', with part_stmts: \n", obj->name);
	dump_part_stmt(obj->stmts, spaces+2);
}

static void dump_part_stmt(PT_part_stmt *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("Part_stmt: named '%s', with type:\n", obj->name);
	dump_type(obj->type, spaces+2);
	dump_part_stmt(obj->prev, spaces);
}


static void dump_array_decl(PT_array_decl *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("Array_decl: Size of\n");
	dump_expr(obj->size, spaces+2);
	dump_array_decl(obj->prev, spaces);
}


#endif

