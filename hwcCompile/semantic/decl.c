#include "decl.h"


#include <stdio.h>
#include <malloc.h>
#include <assert.h>

/*
Converts PT decls into HWC decls. What a good function name.

 - *input is a pointer to the PT_decl to convert
 - *output is a non-initialized HWC_Decl that this function will fill in

Returns nothing, since all meaningful work is done upon *output
*/
void convertPTdeclIntoHWCdecl(PT_decl *input, HWC_Decl *output)
{
	output = malloc(sizeof(HWC_Decl));

	// Extract the "type" of the decl. See pt/type.h for details on what a type can be.
	PT_type *convert = input->type;

	// If this is an array declaration, extract the length of the array
	if(convert->mode == TYPE_ARRAY)
	{
		convertPTexprIntoHWCexpr(convert->len, output->expr);
		convert = convert->base;
	}
	else
		output->expr = NULL;

	// TODO: Allow multi-level arrays
	// ie, this breaks when the "type" of an array is another array.
	if(convert->mode == TYPE_ARRAY)
	{
		fprintf(stderr, "Multi-level arrays are currently not supported in HWC.\n");
		assert(0);
	}

	// Note: We don't set *base_plugType or *base_part yet. Set type so we can check their validity later.
	//   We could check for and set decls of type "bit" here, but we'll need to check the part/plug name
	//   later anyhow, so pass on it for now.
	output->type     = convert->mode;
	output->typeName = convert->ident;

	output->base_plugType = NULL;
	output->base_part     = NULL;

	// Temp dummy value that might be useful later
	output->index = -1;
}


/*
Ensures that the given decl's name hasn't already been used within its namescope.

 - *currDecl is the decl whose name will be checked
 - *currScope is the relevant namescope for this decl
 - isWithinPlug is used for a special check: Whether a part has been declared within a plugtype.
   - Parts can be declared within parts (as subparts) and plugtypes can be declared within parts,
      and plugtypes can be declared within plugtypes, so part within plugtype is the only case to check.
   - isWithinPlug == 1 if the decl is within a plugtype, 0 if not.

Returns 0 if no errors, 1 if errors.
*/
int checkDeclName(HWC_Decl *currDecl, HWC_NameScope *currScope, int isWithinPlug)
{
	// Declared currName up here instead of below TYPE_IDENT because of
	// https://stackoverflow.com/a/18496414
	// Neat!
	HWC_Nameable *currName;
	switch (currDecl->type)
	{
		default:
			// TODO: Add error message
			assert(0);
			break;

		case TYPE_BIT:
			currDecl->base_plugType = &BitType;
			break;

		case TYPE_ARRAY:
			// TODO: I think this is impossible. Remove assert if it isn't.
			assert(0);
			break;

		case TYPE_IDENT:
			currName = nameScope_search(currScope, currDecl->typeName);
			if(currName == NULL)
				return 1;

			// Make sure the name we get back is either a plugtype or a part
			if(currName->plugtype == NULL && currName->part == NULL)
				assert(0);
			// TODO: Report user error instead?

			// Check to make sure a Part declaration isn't inside a plugtype
			if(isWithinPlug == 1 && currName->part != NULL)
			{
				// TODO: Exit this function elegantly instead of through an assert.
				fprintf(stderr, "Part declaration inside a plugtype!\n");
				assert(0);
			}

			// What currDecl field to fill in?
			if(currName->part != NULL)
				currDecl->base_part     = currName->part;
			else
				currDecl->base_plugType = currName->plugtype;

			break;
	}
	return 0;
}
