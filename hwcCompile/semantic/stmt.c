
#include <stdio.h>
#include <assert.h>
#include <malloc.h>

#include "stmt.h"

#include "wiring/fileRange.h"


/*
Takes the given grammar PT_stmt and creates a corresponding semantic HWC_Stmt from it.
The most notable changes are:
 - Conversion from linked list structure to array
 - Compression of struct fields
 - malloc()s memory for the caller
Arguments:
 - *input, a pointer to the statement to convert
 - *output, a pointer to the HWC_Stmt to fill in
Returns an int corresponding to the length of the array of statements
*/
int convertPTstmtIntoHWCstmt(PT_stmt *input, HWC_Stmt **output)
{
	PT_stmt *currPTstmt = input;
	int len = 0;
	while(currPTstmt != NULL)
	{
		len++;
		currPTstmt = currPTstmt->prev;
	}

	*output = malloc(sizeof(HWC_Stmt)*len);
	if(*output == NULL)
	{
		assert(0); // TODO: Better error message?
	}

	// Reset head of list, now that we know the length
	currPTstmt = input;
	int i;
	// Iterate backwards, since all stmt lists from the parser are in reverse order
	for(i = len-1; i >= 0; i--)
	{
		HWC_Stmt *currStmt = *output+i; // TODO: Make sure this indexes by the correct amount

		fr_copy(&currStmt->fr, &currPTstmt->fr);

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
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->stmts, &currStmt->stmtA);
				printf("TODO: How to account for decls within BLOCK stmts?\n");
				break;
			case STMT_CONN:
				convertPTexprIntoHWCexpr(currPTstmt->lHand, &currStmt->exprA);
				convertPTexprIntoHWCexpr(currPTstmt->rHand, &currStmt->exprB);
				break;
			case STMT_FOR:
				// TODO: Should add to nameScope as well?
				currStmt->name  = currPTstmt->forVar;
				convertPTexprIntoHWCexpr(currPTstmt->forBegin, &currStmt->exprA);
				convertPTexprIntoHWCexpr(currPTstmt->forEnd  , &currStmt->exprB);
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->forStmts, &currStmt->stmtA);
				printf("TODO: How to account for decls within FOR stmts?\n");
				break;
			case STMT_IF:
				convertPTexprIntoHWCexpr(currPTstmt->ifExpr, &currStmt->exprA);
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->ifStmts, &currStmt->stmtA);
				currStmt->sizeB = convertPTstmtIntoHWCstmt(currPTstmt->ifElse , &currStmt->stmtB);
				printf("TODO: How to account for decls within IF stmts?\n");
				break;
			case STMT_ELSE:
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->elseStmts, &currStmt->stmtA);
				break;
			case STMT_ASRT:
				convertPTexprIntoHWCexpr(currPTstmt->assertion, &currStmt->exprA);
				break;
		}

		currPTstmt = currPTstmt->prev;
	}


	return len;
}

/*
Ensures that the names used within the given statement are valid within the statement's namescope.

 - *currStmt is the statement to check
 - *currScope is the relevant namescope for the stmt

Returns 0 if no error, >= 1 if errors to indicate how many errors.
*/
int checkStmtName(HWC_Stmt *currStmt, HWC_NameScope *currScope)
{
	int retval = 0;
	HWC_Nameable *currName;
	int i;

	switch(currStmt->mode)
	{
		default:
			assert(0); // TODO: Potentially better error message?
			break;
		case STMT_DECL:
			// NOP, but keeping case here for symmetry
			break;
		case STMT_BLOCK:
			for(i = 0; i < currStmt->sizeA; i++)
				retval += checkStmtName(currStmt->stmtA +i, currScope);
			break;
		case STMT_CONN:
			retval += checkExprName(currStmt->exprA, currScope);
			printf("retval = %d, for %s.\n", retval, currStmt->exprA->name);
			retval += checkExprName(currStmt->exprB, currScope);
			printf("retval = %d, for %s.\n", retval, currStmt->exprB->name);
			break;
	/* STMT_FOR   - uses name, exprA,exprB, stmtA       */
		case STMT_FOR:
			currName = nameScope_search(currScope, currStmt->name);
			// If the name was found, report an error. The name we're checking for should be unique to this for-loop.
			// TODO: Error message
			// TODO: Modify this check later, once we decide if for-loop vars should be added to the namescope or not.
			if(currName != NULL)
				retval++;

			retval += checkExprName(currStmt->exprA, currScope);
			retval += checkExprName(currStmt->exprB, currScope);

			for(i = 0; i < currStmt->sizeA; i++)
				retval += checkStmtName(currStmt->stmtA +i, currScope);
			break;
		case STMT_IF:
			retval += checkExprName(currStmt->exprA, currScope);

			for(i = 0; i < currStmt->sizeA; i++)
				retval += checkStmtName(currStmt->stmtA +i, currScope);
			for(i = 0; i < currStmt->sizeB; i++)
				retval += checkStmtName(currStmt->stmtB +i, currScope);
			break;
		case STMT_ELSE:
			for(i = 0; i < currStmt->sizeA; i++)
				retval += checkStmtName(currStmt->stmtA +i, currScope);
			break;
		case STMT_ASRT:
			retval += checkExprName(currStmt->exprA, currScope);
			break;
	}

	return retval;
}


/*
TODO: Add header comment
*/
int findStmtSize(HWC_Stmt *currStmt)
{
	int retval = 0;
	int i;

	switch(currStmt->mode)
	{
		default:
			assert(0); // TODO: Potentially better error message?
			break;
		case STMT_DECL:
			// NOP, but keeping case here for symmetry
			break;
		case STMT_BLOCK:
			for(i = 0; i < currStmt->sizeA; i++)
				retval += findStmtSize(currStmt->stmtA +i);
			break;
		case STMT_CONN:
			retval += findExprSize(currStmt->exprA);
			retval += findExprSize(currStmt->exprB);
			break;
		case STMT_FOR:
			// Since FOR initializes a variable, we add that to size.
			// TODO: Is this the correct amount to add? The spec specifies for-loops use integers.
			retval += 8;

			retval += findExprSize(currStmt->exprA);
			retval += findExprSize(currStmt->exprB);

			for(i = 0; i < currStmt->sizeA; i++)
				retval += findStmtSize(currStmt->stmtA +i);
			break;
		case STMT_IF:
			retval += findExprSize(currStmt->exprA);

			for(i = 0; i < currStmt->sizeA; i++)
				retval += findStmtSize(currStmt->stmtA +i);
			for(i = 0; i < currStmt->sizeB; i++)
				retval += findStmtSize(currStmt->stmtB +i);
			break;
		case STMT_ELSE:
			for(i = 0; i < currStmt->sizeA; i++)
				retval += findStmtSize(currStmt->stmtA +i);
			break;
		case STMT_ASRT:
			retval += findExprSize(currStmt->exprA);
			break;
	}

	return retval;
}
