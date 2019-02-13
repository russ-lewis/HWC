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

	char     *name;
	HWC_Expr *exprA, *exprB;
	HWC_Stmt *stmtA, *stmtB;
	int       sizeA,  sizeB; // Could we compress sizeA and sizeB with isPub and isSub?
	int       isPub,  isSub; // Aligned, but poor naming. And I assume memory isn't at a premium.
};


int convertPTstmtIntoHWCstmt(PT_stmt *, HWC_Stmt **);
int extractHWCdeclsFromPTstmts(PT_stmt *, HWC_Decl **, HWC_NameScope *, HWC_NameScope *);
int checkStmtName(HWC_Stmt *, HWC_NameScope *);
int findStmtSize(HWC_Stmt *);


void stmt_dump(HWC_Stmt*, int prefixLen);

#endif

