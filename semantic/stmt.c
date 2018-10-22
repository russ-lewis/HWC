#include "stmt.h"
#include "expr.c"

/*
Takes the given grammar PT_stmt and creates a corresponding semantic HWC_Stmt from it.
The most notable changes are:
 - Conversion from linked list structure to array
 - Compression of struct fields
 - malloc()s memory for the caller
Returns an int corresponding to the length of the array of statements
*/
int convertPTstmtIntoHWCstmt(PT_stmt *input, HWC_Stmt *output)
{
	PT_stmt *currPTstmt = input;
	int len = 0;
	while(currPTstmt != NULL)
	{
		currPTstmt = currPTstmt->prev;
		len++;
	}

	output = malloc(sizeof(HWC_Stmt)*len);
	if(output == NULL)
	{
		assert(0); // TODO: Better error message?
	}

	// Reset head of list, now that we know the length
	currPTstmt = input;
	int i;
	// Iterate backwards, since all stmt lists from the parser are in reverse order
	for(i = len-1; i >= 0; i--)
	{
		HWC_Stmt *currStmt = output+i;
		currStmt->mode = currPTstmt->mode;

		switch(currPTstmt->mode)
		{
			default:
				assert(0); // TODO: Potentially better error message?
				break;
			case STMT_DECL:
				currStmt->isPub = currPTstmt->isPublic;
				currStmt->isSub = currPTstmt->isSubpart;
				// TODO
				printf("Remember, Decl is not implemented yet...\n");
				break;
			case STMT_BLOCK:
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->stmts, currStmt->stmtA);
				break;
			case STMT_CONN:
				convertPTexprIntoHWCexpr(currPTstmt->lHand, currStmt->exprA);
				convertPTexprIntoHWCexpr(currPTstmt->rHand, currStmt->exprB);
				break;
			case STMT_FOR:
				currStmt->name  = currPTstmt->forVar;
				convertPTexprIntoHWCexpr(currPTstmt->forBegin, currStmt->exprA);
				convertPTexprIntoHWCexpr(currPTstmt->forEnd  , currStmt->exprB);
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->forStmts, currStmt->stmtA);
			case STMT_IF:
				convertPTexprIntoHWCexpr(currPTstmt->ifExpr, currStmt->exprA);
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->ifStmts, currStmt->stmtA);
				currStmt->sizeB = convertPTstmtIntoHWCstmt(currPTstmt->ifElse , currStmt->stmtB);
				break;
			case STMT_ELSE:
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->elseStmts, currStmt->stmtA);
				break;
			case STMT_ASRT:
				convertPTexprIntoHWCexpr(currPTstmt->assertion, currStmt->exprA);
				break;
		}

		currPTstmt = currPTstmt->prev;
	}


	return len;
}
