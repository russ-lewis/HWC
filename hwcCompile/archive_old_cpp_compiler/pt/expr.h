#ifndef __PARSE_TREE__EXPR_H__INCLUDED__
#define __PARSE_TREE__EXPR_H__INCLUDED__


#include "wiring/fileRange.h"


typedef struct PT_expr      PT_expr;


enum {
	EXPR_IDENT = 101,    // changed the enum definitions, to force non-overlapping values
	EXPR_NUM,
	EXPR_UNARY_NEG,
	EXPR_BOOL,
	EXPR_TWOOP,
	EXPR_BITNOT,
	EXPR_NOT,
	EXPR_DOT,
	EXPR_ARR,
	EXPR_ARR_SLICE,
	EXPR_BIT_TYPE,
	EXPR_FLAG_TYPE,
};

enum {
	OP_EQUALS = 201,    // changed the enum definitions, to force non-overlapping values
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
	OP_CONCAT,
};

struct PT_expr
{
	FileRange fr;

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
	char    *field;

	/* EXPR_ARR, EXPR_ARR_SLICE */
	PT_expr *arrayExpr;
	PT_expr *indexExpr;    // simple array index
	PT_expr *indexExpr1;   // lower slice bounds, could be NULL
	PT_expr *indexExpr2;   // upper slice bounds, could be NULL

	/* EXPR_PAREN */
	PT_expr *paren;
};


// Debug function

void dump_pt_expr(PT_expr *obj, int spaces);

#endif

