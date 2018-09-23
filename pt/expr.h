#ifndef __PARSE_TREE__EXPR_H__INCLUDED__
#define __PARSE_TREE__EXPR_H__INCLUDED__

#include "debug.h"

typedef struct PT_expr      PT_expr;

enum {
	EXPR_IDENT = 1,
};

struct PT_expr
{
	/* choose from the enum above */
	int mode;

	/* EXPR_IDENT */
	char *name;
};

// Debug function

static void dump_expr(PT_expr *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

	printf("Expr: named '%s', mode = %d\n", obj->name, obj->mode);
}

#endif

