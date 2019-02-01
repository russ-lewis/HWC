#ifndef __PARSE_TREE__EXPR_H__INCLUDED__
#define __PARSE_TREE__EXPR_H__INCLUDED__


typedef struct PT_expr      PT_expr;


enum {
	EXPR_IDENT = 1,
	EXPR_NUM,
	EXPR_BOOL,
	EXPR_TWOOP,
	EXPR_BITNOT,
	EXPR_NOT,
	EXPR_DOT,
	EXPR_ARR,
	EXPR_PAREN,

	EXPR__LAST_PARSER_MODE,
};

enum {
	OP_EQUALS,
	OP_NEQUAL,
	OP_BITAND,
	OP_AND,
	OP_BITOR,
	OP_OR,
	OP_XOR,
	/* Explicitly compile-time */
	OP_LESS,
	OP_GREATER,
	OP_LESSEQ,
	OP_GREATEREQ,
	OP_PLUS,
	OP_MINUS,
	OP_TIMES,
	OP_DIVIDE,
	OP_MODULO,
};

struct PT_expr
{
	/* choose from the enum above */
	int mode;

	/* EXPR_IDENT */
	char *name;

	/* EXPR_NUM */
	char *num;

	/* EXPR_BOOL */
	int value;

	/* EXPR_TWOOP */
	int opMode;
	PT_expr *lHand;
	PT_expr *rHand;

	/* EXPR_NOT and EXPR_BITNOT */
	PT_expr *notExpr;

	/* EXPR_DOT */
	PT_expr *dotExpr;
	PT_expr *field;

	/* EXPR_ARR */
	PT_expr *arrayExpr;
	PT_expr *indexExpr;

	/* EXPR_PAREN */
	PT_expr *paren;
};


// Debug function

void dump_pt_expr(PT_expr *obj, int spaces);

#endif

