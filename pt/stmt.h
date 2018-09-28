#ifndef __PARSE_TREE__STMT_H__INCLUDED__
#define __PARSE_TREE__STMT_H__INCLUDED__


typedef struct PT_stmt PT_stmt;

typedef struct PT_expr PT_expr;


enum {
	STMT_CONN = 1,
	STMT_FOR,
	STMT_IF,
	STMT_ELSE,
};

struct PT_stmt
{
	int mode;
	/* linked list, in reverse order of declaration */
	PT_stmt *prev;

	/* STMT_CONN */
	PT_expr *lHand;
	PT_expr *rHand;

	/* STMT_FOR */
	PT_expr  *forVar;
	char		*forBegin;	// Inclusive
	char		*forEnd;		// Exclusive
	PT_stmt  *forStmts;

	/* STMT_IF */
	PT_expr *ifExpr;
	PT_stmt *ifStmts;
	PT_stmt *ifElse;

	/* STMT_ELSE */
	PT_stmt *elseStmts;
};


// Debug functions

void dump_stmt(PT_stmt *obj, int spaces);


#endif

