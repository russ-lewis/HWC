#ifndef __PARSE_TREE__EXPR_H__INCLUDED__
#define __PARSE_TREE__EXPR_H__INCLUDED__


typedef struct PT_expr      PT_expr;

static void dump_expr(PT_expr *, int);

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
	if(obj == NULL)
		return;

	int i;
	for(i = 0; i < spaces; i++)
		printf(" ");
	printf("Expr: %s, mode = %d\n", obj->name, obj->mode);
}

#endif

