#ifndef __PARSE_TREE__EXPR_H__INCLUDED__
#define __PARSE_TREE__EXPR_H__INCLUDED__


typedef struct PT_expr      PT_expr;


enum {
	EXPR_IDENT = 1,
	EXPR_NUM,
	EXPR_EQUAL,

	EXPR__LAST_PARSER_MODE,
};

struct PT_expr
{
	/* choose from the enum above */
	int mode;

	/* EXPR_IDENT */
	char *name;

	/* EXPR_NUM */
	char *num;

	/* EXPR_EQUAL */
	PT_expr *lHand;
	PT_expr *rHand;
};


// Debug function

void dump_expr(PT_expr *obj, int spaces);

#endif

