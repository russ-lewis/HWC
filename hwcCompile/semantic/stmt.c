
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
 - *input, a pointer to the statement to convert
 - *output, a pointer to the HWC_Stmt to fill in
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
				printf("TODO: How to account for decls within FOR stmts?\n");
				break;
			case STMT_IF:
				convertPTexprIntoHWCexpr(currPTstmt->ifExpr, currStmt->exprA);
				currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->ifStmts, currStmt->stmtA);
				currStmt->sizeB = convertPTstmtIntoHWCstmt(currPTstmt->ifElse , currStmt->stmtB);
				printf("TODO: How to account for decls within IF stmts?\n");
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

// TODO: Maybe move to decl.c instead?
/*
Given a list of PT_stmts, extracts all PT_decls and converts them into HWC_Decls.
This is done in a separate step from all other HWC_Stmts because decls are added to the namescope of the part/plugtype.
Returns an int corresponding to the length of the HWC_Decl array malloc'd in "output".
*/
int extractHWCdeclsFromPTstmts(PT_stmt *input, HWC_Decl *output, HWC_NameScope *publ, HWC_NameScope *priv)
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
		// TODO: Can remove this check if the program runs too slow, since the grammar ensures that the only stmts in plugtypes are decls.
		// Use the fact that PlugTypes have no private statements to check if the caller is a PlugType
		else if(priv == NULL)
		{
			// The grammar should prevent non-decl statements from being found in plugtypes, but check just in case.
			fprintf(stderr, "Statement that isn't a declaration found in a plugtype. Should be impossible, but obviously isn't. Crashing.\n");
			assert(0);
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
		HWC_Decl *currHWCdecl = output+count;
		if(currPTstmt->mode == STMT_DECL)
		{
			// TODO: Check if this code writes: [bit a, b, c] backwards or forwards
			PT_decl *currPTdecl = currPTstmt->stmtDecl;
			while(currPTdecl != NULL)
			{
				convertPTdeclIntoHWCdecl(currPTdecl, currHWCdecl);
				HWC_Nameable *thing = malloc(sizeof(HWC_Nameable));
				thing->decl = currHWCdecl;
				// 1st check is for Parts    , makes sure the stmt is public
				// 2nd check if for PlugTypes, makes all decls public
				if(currPTstmt->isPublic == 1 || priv == NULL)
					nameScope_add(publ, currPTdecl->name, thing);
				else
					nameScope_add(priv, currPTdecl->name, thing);

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

	switch(currStmt->mode)
	{
		default:
			assert(0); // TODO: Potentially better error message?
			break;
		case STMT_DECL:
			// NOP, but keeping case here for symmetry
			break;
		case STMT_BLOCK:
			retval += checkStmtName(currStmt->stmtA, currScope);
			break;
		case STMT_CONN:
			retval += checkExprName(currStmt->exprA, currScope);
			retval += checkExprName(currStmt->exprB, currScope);
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

			retval += checkStmtName(currStmt->stmtA, currScope);
			break;
		case STMT_IF:
			retval += checkExprName(currStmt->exprA, currScope);

			retval += checkStmtName(currStmt->stmtA, currScope);
			retval += checkStmtName(currStmt->stmtB, currScope);
			break;
		case STMT_ELSE:
			retval += checkStmtName(currStmt->stmtA, currScope);
			break;
		case STMT_ASRT:
			retval += checkExprName(currStmt->exprA, currScope);
			break;
	}

	return retval;
}
