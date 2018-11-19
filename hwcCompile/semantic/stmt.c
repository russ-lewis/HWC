
#include "stmt.h"

#include <stdio.h>
#include <assert.h>
#include <malloc.h>

/*
Takes the given grammar PT_stmt and creates a corresponding semantic HWC_Stmt from it.
The most notable changes are:
 - Conversion from linked list structure to array
 - Compression of struct fields
 - malloc()s memory for the caller
Arguments:
 - input, a pointer to the statement to convert
 - output, a pointer to the HWC_Stmt to fill in
Returns an int corresponding to the length of the array of statements
*/
int convertPTstmtIntoHWCstmt(PT_stmt *input, HWC_Stmt *output)
{
	PT_stmt *currPTstmt = input;
	int len = 0;
	while(currPTstmt != NULL)
	{
		len++;
		currPTstmt = currPTstmt->prev;
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
		HWC_Stmt *currStmt = output+i; // TODO: Make sure this indexes by the correct amount
		currStmt->mode = currPTstmt->mode;

		switch(currPTstmt->mode)
		{
			default:
				assert(0); // TODO: Potentially better error message?
				break;
			case STMT_DECL:
				// NOP, but keeping case here for symmetry
				break;
			case STMT_BLOCK:
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->stmts, currStmt->stmtA);
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

/*
TODO: Header comment
*/
int extractHWCdeclsFromPTstmts(PT_stmt *input, HWC_Decl *output)
{
	PT_stmt *currPTstmt = input;
	int len = 0;

	while(currPTstmt != NULL)
	{
		if(currPTstmt->mode == STMT_DECL)
		{
			// Nested while() because PT_decls have their own list of decls.
			PT_decl *currPTdecl = currPTstmt->stmtDecl;
			while(currPTdecl != NULL)
			{
				len++;
				currPTdecl = currPTdecl->prev;
			}
		}
		currPTstmt = currPTstmt->prev;
	}

	output = malloc(sizeof(HWC_Decl)*len);
	if(output == NULL)
	{
		assert(0); // TODO: Better error message?
	}

	// Reset to beginning of list
	currPTstmt = input;
	// Iterate through the backwards list again, but use "count" to write the output in forward order.
	int count = len-1;
	while(currPTstmt != NULL)
	{
		HWC_Decl *currDecl = output+count;
		if(currPTstmt->mode == STMT_DECL)
		{
			// TODO: Check if this code writes: [bit a, b, c] backwards or forwards
			PT_decl *currPTdecl = currPTstmt->stmtDecl;
			while(currPTdecl != NULL)
			{
				convertPTdeclIntoHWCdecl(currPTdecl, currDecl);
				count--;
				currPTdecl = currPTdecl->prev;
			}
		}
		currPTstmt = currPTstmt->prev;
	}

	// Make sure that, by the end of this, the last index count wrote to was 0
	// +1 to offset the subtraction done after writing to 0
	assert(count+1 == 0);

	return len;
}
