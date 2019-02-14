#ifndef __SEMANTIC_STMT_H__INCLUDED__
#define __SEMANTIC_STMT_H__INCLUDED__


#include <pt/stmt.h>    // we'll re-use the modes from the parser

#include "wiring/fileRange.h"

#include "names.h"
#include "expr.h"
#include "decl.h"



typedef struct HWC_Stmt HWC_Stmt;
struct HWC_Stmt
{
	FileRange fr;

	int mode;

	/* STMT_DECL  - uses isPub, isSub,                  */
	/* STMT_BLOCK - uses                    stmtA       */
	/* STMT_CONN  - uses       exprA,exprB              */
	/* STMT_FOR   - uses name, exprA,exprB, stmtA       */
	/* STMT_IF    - uses       exprA,       stmtA,stmtB */
	/* STMT_ELSE  - uses                    stmtA       */
	/* STMT_ASRT  - uses       exprA                    */
	// Any STMT type that uses stmtA or stmtB uses sizeA and sizeB as well

	// Used mostly with for-loops, as the iteration variable name.
	char     *name;
	// Relevant exprs for this statement.
	HWC_Expr *exprA, *exprB;
	// Used by BLOCK, FOR, IF, and ELSE to point to a list of more stmts within them
	HWC_Stmt *stmtA, *stmtB;
	// Contains the length of the above list of stmts
	int       sizeA,  sizeB;
	// The name scope for the above list of stmts.
	// Allows disjoint curly-bracket stmts to declare the same variable without conflicting.
	HWC_NameScope *namesA, *namesB;
	// Is the declaration public? Is the declaration a subpart?
	int isPublic,  isSubpart;

};


int convertPTstmtIntoHWCstmt(PT_stmt *, HWC_Stmt **);
int extractHWCdeclsFromPTstmts(PT_stmt *, HWC_Decl **, HWC_NameScope *, HWC_NameScope *);
int checkStmtName(HWC_Stmt *, HWC_NameScope *);
int findStmtSize(HWC_Stmt *);


void stmt_dump(HWC_Stmt*, int prefixLen);

#endif

