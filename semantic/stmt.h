#ifndef __SEMANTIC_STMT_H__INCLUDED__
#define __SEMANTIC_STMT_H__INCLUDED__


#include <pt/stmt.h>    // we'll re-use the modes from the parser

#include "names.h"
#include "expr.h"
#include "stmt.h"


typedef struct HWC_Stmt HWC_Stmt;
struct HWC_Stmt
{
	int mode;

	/* STMT_CONN - uses       exprA,exprB       */
	/* STMT_FOR  - uses name, exprA,exprB, stmt */

	char     *name;
	HWC_Expr *exprA, *exprB;
	HWC_Stmt *stmt;
};


#endif

