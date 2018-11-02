
#include "stmt.h"


#include <stdio.h>
#include <malloc.h>
#include <assert.h>

/*
Takes the given grammar PT_stmt and creates a corresponding semantic HWC_Stmt from it.
The most notable changes are:
 - Conversion from linked list structure to array
 - Compression of struct fields
 - malloc()s memory for the caller
Arguments:
 - input, a pointer to the statement to convert
 - output, a pointer to the HWC_Stmt to fill in
 - caller, 
***NOTE: Could remove output parameter, because caller contains output (see function call in phase10_part.c)
Returns an int corresponding to the length of the array of statements
*/
int convertPTstmtIntoHWCstmt(PT_stmt *input, HWC_Stmt *output, HWC_Part *caller)
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
				HWC_Nameable *nameableDecl = malloc(sizeof(HWC_Nameable));
					assert(thing != NULL);   // TODO: better error checking
				// thing->Decl = whatever we make
				nameScope_add(caller->publicNames, currPTstmt->stmtDecl->name, nameableDecl);
				currStmt->isPub = currPTstmt->isPublic;
				currStmt->isSub = currPTstmt->isSubpart;
				// currStmt->decl = conversionFunction()
				// TODO
				printf("Remember, Decl is not implemented yet...\n");
				break;
			case STMT_BLOCK:
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->stmts, currStmt->stmtA, fileScope, caller);
				break;
			case STMT_CONN:
				convertPTexprIntoHWCexpr(currPTstmt->lHand, currStmt->exprA);
				convertPTexprIntoHWCexpr(currPTstmt->rHand, currStmt->exprB);
				break;
			case STMT_FOR:
				// TODO: Should add to nameScope as well?
				currStmt->name  = currPTstmt->forVar;
				convertPTexprIntoHWCexpr(currPTstmt->forBegin, currStmt->exprA);
				convertPTexprIntoHWCexpr(currPTstmt->forEnd  , currStmt->exprB);
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->forStmts, currStmt->stmtA, fileScope, caller);
			case STMT_IF:
				convertPTexprIntoHWCexpr(currPTstmt->ifExpr, currStmt->exprA);
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->ifStmts, currStmt->stmtA, fileScope, caller);
				currStmt->sizeB = convertPTstmtIntoHWCstmt(currPTstmt->ifElse , currStmt->stmtB, fileScope, caller);
				break;
			case STMT_ELSE:
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->elseStmts, currStmt->stmtA, fileScope, caller);
				break;
			case STMT_ASRT:
				convertPTexprIntoHWCexpr(currPTstmt->assertion, currStmt->exprA);
				break;
		}

		currPTstmt = currPTstmt->prev;
	}


	return len;
}
