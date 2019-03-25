#include <stdio.h>
#include <malloc.h>
#include <assert.h>

#include "decl.h"

#include "semantic/part.h"
#include "semantic/phase20.h"

#include "wiring/fileRange.h"



/*
 * Given a list of PT_stmts, extracts all PT_decls and converts them into
 * HWC_Decls.
 *
 * This is done in a separate step from all other HWC_Stmts because decls are
 * added to the namescope of the part/plugtype.
 *
 * Returns an int corresponding to the length of the HWC_Decl array malloc'd
 * in "output".
 */
int extractHWCdeclsFromPTstmts(PT_stmt *input, HWC_Decl **output,
                               HWC_NameScope *publ, HWC_NameScope *priv)
{
	PT_stmt *currPTstmt = input;
	int len = 0;

	while(currPTstmt != NULL)
	{
		// used inside one case of the switch
		PT_decl *currPTdecl;

		/* If the caller didn't pass us a private nameScope, then we
		 * know implicitly that this is a declaration inside a
		 * plugtype.  In that case, non-declaration statements should
		 * be illegal (for now, until we add support for static if).
		 */
		if (priv == NULL)
			assert(currPTstmt->mode == STMT_DECL);

		switch (currPTstmt->mode)
		{
		default:
			assert(0);

		case STMT_CONN:
		case STMT_ASRT:
			break;    // no declarations possible

		case STMT_DECL:
			// Nested while() because PT_decls have their own list of decls.
			currPTdecl = currPTstmt->declList;
			while(currPTdecl != NULL)
			{
				len++;
				currPTdecl = currPTdecl->next;
			}
			break;

		case STMT_IF:
		case STMT_FOR:
		case STMT_BLOCK:
			printf("TODO: %s(): Implement declarations inside of IF/FOR/BLOCK statements.\n", __func__);
			break;
		}

		currPTstmt = currPTstmt->next;
	}

	*output = malloc(sizeof(HWC_Decl)*len);
	if(*output == NULL)
	{
		assert(0); // TODO: Better error message?
	}


	// Iterate through the list again, but use "count" to keep track of
	// where we are as we convert the decls.
	int count = 0;
	for (currPTstmt  = input;
	     currPTstmt != NULL;
	     currPTstmt  = currPTstmt->next)
	{
		if (currPTstmt->mode != STMT_DECL)
			continue;   // nothing to do in this loop

		// TODO: Check if this code writes: [bit a, b, c] backwards or forwards
		PT_decl *currPTdecl = currPTstmt->declList;
		while(currPTdecl != NULL)
		{
			HWC_Decl *currHWCdecl = (*output)+count;

			int retval = convertPTdeclIntoHWCdecl(currPTdecl,
			                                      currPTstmt->declType,
			                                      currPTstmt->isMemory,
			                                      currHWCdecl);
				assert(retval == 0);    // TODO: convert this function to report errors when necessary.

			HWC_Nameable *thing = malloc(sizeof(HWC_Nameable));
			fr_copy(&thing->fr, &currHWCdecl->fr);
			thing->decl = currHWCdecl;

			/* if isPublic, then we definitely want to post
			 * this name to the public namescope.  This
			 * applies to *any* declaration within a
			 * plugtype, and also public declarations
			 * within a part.
			 */
			if (currPTstmt->isPublic)
				nameScope_add(publ, currPTdecl->name, thing);

			/* if the private nameScope is defined, then we
			 * *also* post this name to the private scope.
			 * Note that it is perfectly normal to post the
			 * same Thing to the both scopes; this happens
			 * for public plugs on parts.
			 */
			if (priv != NULL)
				nameScope_add(priv, currPTdecl->name, thing);

			count++;
			currPTdecl = currPTdecl->next;
		}
	}

	// Sanity check that we filled out exactly the number of decls we
	// expected.
	assert(count == len);

	return len;
}


/*
 * Converts PT decls into HWC decls. What a good function name.
 * 
 *  - *input is a pointer to the PT_decl to convert
 *  - **output_out is a non-initialized HWC_Decl that this function will fill in
 * 
 * Returns nothing, since all meaningful work is done upon *output
 */
int convertPTdeclIntoHWCdecl(PT_decl *input,
                             PT_expr *type,
                             int      isMemory,
	                     HWC_Decl *output)
{
	fr_copy(&output->fr, &input->fr);
	sizes_init(&output->sizes);
	sizes_init(&output->offsets);

	// Extract the "type" of the decl. See pt/type.h for details on what a type can be.
	PT_expr *convert = type;

	// Make sure convert has a proper mode.
	switch (convert->mode)
	{
		default:
			fprintf(stderr, "Bad mode! Value of [%d].\n", convert->mode);
			assert(0);
			break;

		case EXPR_BIT_TYPE:
		case EXPR_ARR:
		case EXPR_IDENT:
			break;
	}


	// If this is an array declaration, extract the length of the array.
	// Then, we'll update the 'convert' pointer, so that we can focus on
	// the base type and do the conversion
	if(convert->mode == EXPR_ARR)
	{
		convertPTexprIntoHWCexpr(convert->indexExpr, &output->expr);
		convert = convert->arrayExpr;
	}
	else
		output->expr = NULL;


	// TODO: Allow multi-level arrays
	// ie, this breaks when the "type" of an array is another array.
	if(convert->mode == EXPR_ARR)
	{
		fprintf(stderr, "%s:%d:%d: Multi-level arrays are currently not supported in HWC.\n",
		        convert->fr.filename,
		        convert->fr.s.l, convert->fr.s.c);
		return 1;
	}


	// Note: We don't set *base_plugType or *base_part yet. Set type so we can check their validity later.
	//   We could check for and set decls of type "bit" here, but we'll need to check the part/plug name
	//   later anyhow, so pass on it for now.
	output->type     = convert->mode;
	output->typeName = convert->name;   // used for IDENT, ignored for BIT_TYPE
	  fr_copy(&output->typeName_fr, &type->fr);

	output->isMem    = isMemory;

	output->base_plugType = NULL;
	output->base_part     = NULL;

	return 0;
}


/*
 * Ensures that the given decl's name hasn't already been used within its namescope.
 * 
 *  - *currDecl is the decl whose name will be checked
 *  - *currScope is the relevant namescope for this decl
 *  - isWithinPlug is used for a special check: Whether a part has been declared within a plugtype.
 *    - A decl within a part might refer to either a part or a plugtype
 *    - A decl within a plugtype must only refer to other plugtypes
 *    - isWithinPlug == 1 if the decl is within a plugtype, 0 if not.
 * 
 * Returns 0 if no errors, 1 if errors.
 *     (This will print out an appropriate error message, so the caller should
 *      not print anything out, but it *should* terminate with an error to its
 *      own caller.)
 */
int checkDeclName(HWC_Decl *currDecl, HWC_NameScope *currScope, int isWithinPlug)
{
	HWC_Nameable *currName;
	switch (currDecl->type)
	{
		default:
			fprintf(stderr, "currDecl->type == %d\n", currDecl->type);
			fprintf(stderr, "currDecl->typeName == %s\n", currDecl->typeName);
			fprintf(stderr, "currDecl was not of type bit, array, or ident.\n");
			assert(0);
			break;

		case EXPR_BIT_TYPE:
			currDecl->base_plugType = &BitType;
			break;

		case EXPR_ARR:
			fprintf(stderr, "-- TODO: %s(): Implement array types.\n", __func__);
			return 1;

		case EXPR_IDENT:
			// Does the type name exist in our current NameScope?
			currName = nameScope_search(currScope, currDecl->typeName);
			if(currName == NULL)
			{
				fprintf(stderr, "%s:%d:%d: Symbol '%s' not found\n",
				        currDecl->typeName_fr.filename,
				        currDecl->typeName_fr.s.l, currDecl->typeName_fr.s.c,
				        currDecl->typeName);
				return 1;
			}

			// TODO: make this common code.  Right now, we check the declaring-type several times (if we have multiple names declared in the same statement).  This is harmless but wasteful.

			// Make sure the name we get back is either a plugtype or a part
			if(currName->plugtype == NULL && currName->part == NULL)
			{
				fprintf(stderr, "%s:%d:%d: Symbol '%s' is neither a part nor a plugtype.\n",
				        currDecl->typeName_fr.filename,
				        currDecl->typeName_fr.s.l, currDecl->typeName_fr.s.c,
				        currDecl->typeName);
				return 1;
			}

			// Check to make sure a Part declaration isn't inside a plugtype
			if(isWithinPlug == 1 && currName->part != NULL)
			{
				fprintf(stderr, "%s:%d:%d: Parts may not be fields inside plugtypes.\n",
				        currDecl->fr.filename,
				        currDecl->fr.s.l, currDecl->fr.s.c);
				return 1;
			}

			// What currDecl field to fill in?
			if(currName->part != NULL)
				currDecl->base_part     = currName->part;
			else
				currDecl->base_plugType = currName->plugtype;

			break;
	}


	/* recurse into the array index expression (if any); check the names
	 * in there, and also figure out the type of the expression (it better
	 * be an integer!
	 */
	if (currDecl->expr != NULL)
	{
		int retval = semPhase20_expr(currDecl->expr, currScope);
		if (retval != 0)
			return retval;

		if (currDecl->expr->val.type != EXPR_VALTYPE_INT)
		{
printf("%d\n", currDecl->expr->val.type);
			fprintf(stderr, "%s:%d:%d: Expression does not resolve to an compile-time integer.\n",
			        currDecl->expr->fr.filename,
			        currDecl->expr->fr.s.l, currDecl->expr->fr.s.c);
			return 1;
		}
	}

	return 0;
}



int semPhase30_decl(HWC_Decl *input, int isWithinPlug)
{
	sizes_set_zero(&input->sizes);

	/* base size.  This will be multiplied, in some cases that follow */

	if(input->base_plugType != NULL)
	{
		int retval = semPhase30_plugtype(input->base_plugType);
		if (retval != 0)
			return retval;

		assert(input->base_plugType->sizeBits != -1);

		sizes_set_zero(&input->sizes);
		input->sizes.bits = input->base_plugType->sizeBits;
	}
	else if(input->base_part != NULL)
	{
		if(isWithinPlug == 1)
		{
			fprintf(stderr, "%s:%d:%d: Part included as a field in a plugtype.  (Plugtypes can only include other plugtypes as fields.)\n",
			        input->expr->fr.filename,
			        input->expr->fr.s.l, input->expr->fr.s.c);
		}
		else
		{
			int retval = semPhase30_part(input->base_part);
			if (retval != 0)
				return retval;

			sizes_copy(&input->sizes, &input->base_part->sizes);
		}
	}
	else
	{
		assert(0); // TODO: Error message
		// Likely a compiler error than a user error, since these fields should have been filled in phase20
	}


	/* now that the base size is determined, we'll check to see if this
	 * is memory and/or an array, since those require special handling.
	 * Note that we need to handle the array case first, just in case
	 * we have an array memory cell.
	 */

	if (input->expr != NULL)
	{
		/* we must have already run phase 20 on this expression, back
		 * in phase 20 of the code!
		 */
		assert(input->expr->val.type != EXPR_VALTYPE_INVALID);

		if (expr_evaluate(input->expr, 1) != 0)
			return 1;

		if (input->expr->val.intVal < 0)
		{
			fprintf(stderr, "%s:%d:%d: Array size was negative (size=%d)\n",
			        input->expr->fr.filename,
			        input->expr->fr.s.l, input->expr->fr.s.c,
			        input->expr->val.intVal);
			return 1;
		}

		if (input->expr->val.intVal == 0)
		{
			fprintf(stderr, "%s:%d:%d: Array size was zero.\n",
			        input->expr->fr.filename,
			        input->expr->fr.s.l, input->expr->fr.s.c);
			return 1;
		}

		input->sizes.bits *= input->expr->val.intVal;
	}

	/* if memory, then double the size.  Also, allocate a memory object,
	 * and space in the memBits.
	 */
	if(input->isMem == 1)
	{
		/* memory should never be possible if the underlying type is
		 * a part.  And plugtypes should never have sizes in anything
		 * other than bits.
		 */
		assert(input->base_plugType != NULL);
		assert(input->sizes.memoryObjs == 0);
		assert(input->sizes.memBits    == 0);

		input->sizes.memoryObjs = 1;
		input->sizes.memBits    = input->sizes.bits;

		input->sizes.bits *= 2;
	}


	return 0;
}


int expr_evaluate(HWC_Expr *expr, int force)
{
	assert(expr->val.type != EXPR_VALTYPE_INVALID);

	if (expr->val.ready)
		return 0;

	printf("%d\n", expr->mode);
	assert(0);   // TODO
}

