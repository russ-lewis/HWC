#ifndef __PARSE_TREE__STMT_H__INCLUDED__
#define __PARSE_TREE__STMT_H__INCLUDED__


#include "wiring/fileRange.h"


typedef struct PT_stmt PT_stmt;
typedef struct PT_decl PT_decl;

typedef struct PT_expr PT_expr;
typedef struct PT_type PT_type;


enum {
	STMT_DECL = 301,    // changed the enum definitions, to force non-overlapping values
	STMT_CONN,
	STMT_IF,
	STMT_FOR,
	STMT_BLOCK,
	STMT_ASRT,

	// used only by the semantic phase
	STMT_NOP,
};

struct PT_stmt
{
	FileRange fr;

	int mode;

	/* linked list, in the order of declaration (used to be reversed, but not anymore!) */
	PT_stmt *next;

	/* STMT_DECL */
	int isPublic;       // 1 for true, 0 for false
	int isSubpart;      // 1 for true, 0 for false
	int isMemory;       // 1 for true, 0 for false
	PT_expr *declType;
	PT_decl *declList;


	/* STMT_BLOCK */
	PT_stmt *stmts;     // is a linked list

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

	/* STMT_ASRT */
	PT_expr *assertion;
};



/* this struct is used to store the parse tree for the nonterminals
 * 'decl_fields', as well as its various sub-nonterminals inside that.
 * Each decl_field struct represents a single name in a comma-separated
 * list of names, inside a single declaration statement.  It contains
 * the type of the statement (which is identical for all of the decls
 * in a list), as well as the name and array metadata (which is NULL
 * if there were no per-name array suffixes).
 */
struct PT_decl
{
	FileRange fr;

	/* linked list of decls */
	PT_decl *next;

	char *name;

	PT_expr *init;
};



// Debug functions

void dump_pt_stmt(PT_stmt *obj, int spaces);
void dump_pt_decl(PT_decl *obj, int spaces);


#endif

