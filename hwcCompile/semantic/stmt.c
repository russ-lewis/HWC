
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>

#include "semantic/phase10.h"
#include "semantic/phase20.h"
#include "semantic/phase30.h"
#include "semantic/phase35.h"

#include "semantic/stmt.h"

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
		currPTstmt = currPTstmt->next;
	}

	*output = malloc(sizeof(HWC_Stmt)*len);
	if(*output == NULL)
	{
		assert(0); // TODO: Better error message?
	}

	// Reset head of list, now that we know the length
	currPTstmt = input;
	int i;

	for(i=0; i < len; i++)
	{
		HWC_Stmt *currStmt = *output+i; // TODO: Make sure this indexes by the correct amount

		fr_copy   (&currStmt->fr, &currPTstmt->fr);
		sizes_init(&currStmt->sizes);
		sizes_init(&currStmt->offsets);

		currStmt->mode = currPTstmt->mode;
		// TODO: Initialize other variables of currStmt?

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
				fprintf(stderr, "TODO: Decls within BLOCK stmts are not accounted for yet.\n");
				break;

		case STMT_CONN:
			currStmt->exprA = phase10_expr(currPTstmt->lHand);
			currStmt->exprB = phase10_expr(currPTstmt->rHand);

			if (currStmt->exprA == NULL || currStmt->exprB == NULL)
				assert(0);   // TODO: error handling
			break;

		case STMT_FOR:
			// TODO: Should add to nameScope as well?
			currStmt->name  = currPTstmt->forVar;

			currStmt->exprA = phase10_expr(currPTstmt->forBegin);
			currStmt->exprB = phase10_expr(currPTstmt->forEnd);
			if (currStmt->exprA == NULL || currStmt->exprB == NULL)
				assert(0);   // TODO: error handling

			currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->forStmts, &currStmt->stmtA);
			fprintf(stderr, "TODO: Decls within FOR stmts are not accounted for yet.\n");
			break;

		case STMT_IF:
			currStmt->exprA = phase10_expr(currPTstmt->ifExpr);
			if (currStmt->exprA == NULL)
				assert(0);   // TODO: error handling

			currStmt->sizeA = convertPTstmtIntoHWCstmt(currPTstmt->ifStmts, &currStmt->stmtA);
			currStmt->sizeB = convertPTstmtIntoHWCstmt(currPTstmt->ifElse , &currStmt->stmtB);
			fprintf(stderr, "TODO: Decls within IF stmts are not accounted for yet.\n");
			break;

		case STMT_ASRT:
			currStmt->exprA = phase10_expr(currPTstmt->assertion);
			break;
		}

		currPTstmt = currPTstmt->next;
	}


	return len;
}

/*
 * Ensures that the names used within the given statement are valid within the statement's namescope.
 * 
 *  - *currStmt is the statement to check
 *  - *currScope is the relevant namescope for the stmt
 * 
 * Returns 0 if no error, >= 1 if errors to indicate how many errors.
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
			retval += semPhase20_expr(currStmt->exprA, currScope);
			retval += semPhase20_expr(currStmt->exprB, currScope);
			break;

	/* STMT_FOR   - uses name, exprA,exprB, stmtA       */
		case STMT_FOR:
			currName = nameScope_search(currScope, currStmt->name);
			// If the name was found, report an error. The name we're checking for should be unique to this for-loop.
			// TODO: Error message
			// TODO: Modify this check later, once we decide if for-loop vars should be added to the namescope or not.
			if(currName != NULL)
			{
				fprintf(stderr, "%s:%d:%d: Symbol '%s' is the same as a prior declaration at %s:%d:%d.  This 'shadowing' of names is illegal in HWC.\n",
				        currStmt->fr.filename,
				        currStmt->fr.s.l, currStmt->fr.s.c,
				        currStmt->name,
				        currName->fr.filename,
				        currName->fr.s.l, currName->fr.s.c);
				retval++;
			}

			fprintf(stderr, "TODO: Remove this syntax-error mark when we implement support for for() loops.\n");
			retval++;

			retval += semPhase20_expr(currStmt->exprA, currScope);
			retval += semPhase20_expr(currStmt->exprB, currScope);

			for(i = 0; i < currStmt->sizeA; i++)
				retval += checkStmtName(currStmt->stmtA +i, currScope);
			break;

		case STMT_IF:
			retval += semPhase20_expr(currStmt->exprA, currScope);

			for(i = 0; i < currStmt->sizeA; i++)
				retval += checkStmtName(currStmt->stmtA +i, currScope);
			for(i = 0; i < currStmt->sizeB; i++)
				retval += checkStmtName(currStmt->stmtB +i, currScope);
			break;
		case STMT_ASRT:
			retval += semPhase20_expr(currStmt->exprA, currScope);
			break;
	}

	return retval;
}



int semPhase30_stmt(HWC_Stmt *currStmt)
{
	int retval = 0;
	int i;

	sizes_set_zero(&currStmt->sizes);

	switch(currStmt->mode)
	{
	default:
		assert(0); // TODO: Potentially better error message?
		break;

	case STMT_DECL:
		// NOP, but keeping case here for symmetry
		break;

	case STMT_BLOCK:
		for(i=0; i < currStmt->sizeA; i++)
		{
			retval += semPhase30_stmt(&currStmt->stmtA[i]);
			sizes_inc(&currStmt->sizes, &currStmt->stmtA[i].sizes);
		}
		break;

	case STMT_CONN:
		// exprA: lhs
		// exprB: rhs

		retval  = semPhase30_expr(currStmt->exprA);
		retval += semPhase30_expr(currStmt->exprB);

		// this should be enforced earlier, by double-checking that
		// they are both the same type.
		if (retval == 0)
			assert(currStmt->exprA->retvalSize == currStmt->exprB->retvalSize);

		sizes_add(&currStmt->sizes,
		          &currStmt->exprA->sizes, &currStmt->exprB->sizes);

		// add in a connection component to the total size
		currStmt->sizes.conns++;
		break;

	case STMT_FOR:
assert(0);   // TODO
#if 0
		// Since FOR initializes a variable, we add that to size.
		// TODO: Is this the correct amount to add? The spec specifies for-loops use integers.
		retval += 8;

		retval += findExprSize(currStmt->exprA, currOffset, numLogic, 0);
		retval += findExprSize(currStmt->exprB, currOffset, numLogic, 0);

		for(i = 0; i < currStmt->sizeA; i++)
			retval += findStmtSize(currStmt->stmtA +i, currOffset, numConn, numLogic, numAssert);
#endif
		break;

	case STMT_IF:
		retval += semPhase30_expr(currStmt->exprA);
		sizes_copy(&currStmt->sizes, &currStmt->exprA->sizes);

		for(i = 0; i < currStmt->sizeA; i++)
		{
			retval += semPhase30_stmt(&currStmt->stmtA[i]);
			sizes_inc(&currStmt->sizes, &currStmt->stmtA[i].sizes);
		}

		for(i = 0; i < currStmt->sizeB; i++)
		{
			retval += semPhase30_stmt(&currStmt->stmtB[i]);
			sizes_inc(&currStmt->sizes, &currStmt->stmtB[i].sizes);
		}
		break;

	case STMT_ASRT:
		retval += semPhase30_expr(currStmt->exprA);

		sizes_copy(&currStmt->sizes, &currStmt->exprA->sizes);
		currStmt->sizes.asserts++;
		break;
	}

	return retval;
}



int semPhase35_stmt(HWC_Stmt *currStmt)
{
	int retval = 0;
	int i;

	/* the caller has initialized the offset */
	assert(sizes_are_ready(&currStmt->offsets));

	switch(currStmt->mode)
	{
	default:
		assert(0); // TODO: Potentially better error message?
		break;

	case STMT_DECL:
		// NOP, but keeping case here for symmetry
		break;

	case STMT_BLOCK:
		if (currStmt->sizeA > 0)
		{
			sizes_copy(&currStmt->stmtA[0].offsets,
			           &currStmt->offsets);
			retval += semPhase35_stmt(&currStmt->stmtA[0]);

			int i;
			for(i=1; i < currStmt->sizeA; i++)
			{
				sizes_add(&currStmt->stmtA[i].offsets,
				          &currStmt->stmtA[i-1].offsets,
				          &currStmt->stmtA[i-1].sizes);
				retval += semPhase35_stmt(&currStmt->stmtA[i]);
			}
		}
		break;

	case STMT_CONN:
		// exprA: lhs
		// exprB: rhs

		sizes_copy(&currStmt->exprA->offsets, &currStmt->offsets);
		retval  = semPhase35_expr(currStmt->exprA, 1);

		sizes_add(&currStmt->exprB->offsets,
		          &currStmt->exprA->offsets, &currStmt->exprA->sizes);
		retval += semPhase35_expr(currStmt->exprB, 0);
		break;

	case STMT_FOR:
assert(0);   // TODO
#if 0
		// Since FOR initializes a variable, we add that to size.
		// TODO: Is this the correct amount to add? The spec specifies for-loops use integers.
		retval += 8;

		retval += findExprSize(currStmt->exprA, currOffset, numLogic, 0);
		retval += findExprSize(currStmt->exprB, currOffset, numLogic, 0);

		for(i = 0; i < currStmt->sizeA; i++)
			retval += findStmtSize(currStmt->stmtA +i, currOffset, numConn, numLogic, numAssert);
#endif
		break;

	case STMT_IF:
		retval += semPhase30_expr(currStmt->exprA);
		sizes_copy(&currStmt->sizes, &currStmt->exprA->sizes);

		for(i = 0; i < currStmt->sizeA; i++)
		{
			retval += semPhase30_stmt(&currStmt->stmtA[i]);
			sizes_inc(&currStmt->sizes, &currStmt->stmtA[i].sizes);
		}

		for(i = 0; i < currStmt->sizeB; i++)
		{
			retval += semPhase30_stmt(&currStmt->stmtB[i]);
			sizes_inc(&currStmt->sizes, &currStmt->stmtB[i].sizes);
		}
		break;

	case STMT_ASRT:

		/*
		currStmt->offsets.bits = *numAssert;
		*numAssert += 1;
		retval += findExprSize(currStmt->exprA, currOffset, numLogic, 0);
		*/

		retval += semPhase30_expr(currStmt->exprA);
		sizes_copy(&currStmt->sizes, &currStmt->exprA->sizes);

		for(i = 0; i < currStmt->sizeA; i++)
		{
			printf("HERE\n");
			retval += semPhase30_stmt(&currStmt->stmtA[i]);
			sizes_inc(&currStmt->sizes, &currStmt->stmtA[i].sizes);
		}

		for(i = 0; i < currStmt->sizeB; i++)
		{
			retval += semPhase30_stmt(&currStmt->stmtB[i]);
			sizes_inc(&currStmt->sizes, &currStmt->stmtB[i].sizes);
		}
		break;
	}

	return retval;
}

