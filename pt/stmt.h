#ifndef __PARSE_TREE__STMT_H__INCLUDED__
#define __PARSE_TREE__STMT_H__INCLUDED__


typedef struct PT_stmt PT_stmt;
typedef struct PT_decl PT_decl;

typedef struct PT_expr PT_expr;


enum {
	STMT_DECL = 1,
	STMT_CONN,
	STMT_FOR,
	STMT_IF,
	STMT_ELSE,
};

struct PT_stmt
{
	int mode;
	/* linked list, in reverse order of declaration */
	PT_stmt *prev;

	/* STMT_DECL */
	int isPublic;       // 1 for true, 0 for false
	PT_decl *stmtDecl;

	/* STMT_CONN */
	PT_expr *lHand;
	PT_expr *rHand;

	/* STMT_FOR */
	char    *forVar;
	PT_expr *forBegin;    // Inclusive
	PT_expr *forEnd;      // Exclusive
	PT_stmt *forStmts;

	/* STMT_IF */
	PT_expr *ifExpr;
	PT_stmt *ifStmts;
	PT_stmt *ifElse;

	/* STMT_ELSE */
	PT_stmt *elseStmts;
};


struct PT_decl
{
	/* linked list, in reverse order of declaration */
	/* This should be null if this is part of a PT_stmt */
	PT_decl *prev;

	PT_type *type;
	char *name;
	PT_array_decl *arraySuffix;
};

// Debug functions

void dump_pt_stmt(PT_stmt *obj, int spaces);
void dump_pt_decl(PT_decl *obj, int spaces);


#endif

