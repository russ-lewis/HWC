#ifndef __PARSE_TREE__STMT_H__INCLUDED__
#define __PARSE_TREE__STMT_H__INCLUDED__


typedef struct PT_stmt PT_stmt;

typedef struct PT_expr PT_expr;


enum {
	STMT_CONN = 1,
	STMT_FOR,
	STMT_IF,
};

struct PT_stmt
{
	int mode;

	/* STMT_CONN */
	PT_expr *lHand;
	PT_expr *rHand;

	/* STMT_FOR */
	// TODO

	/* STMT_FOR */
	// TODO
};


// Debug functions

void dump_stmt(PT_stmt *obj, int spaces);


#endif

