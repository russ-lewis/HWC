#include "decl.h"


#include <stdio.h>
#include <malloc.h>
#include <assert.h>

/*
TODO: Change header comment
*/
void convertPTdeclIntoHWCdecl(PT_decl *input, HWC_Decl *output)
{
	output = malloc(sizeof(HWC_Decl));

	PT_type *convert = input->type;
	if(convert->mode == TYPE_ARRAY)
	{
		convertPTexprIntoHWCexpr(convert->len, output->expr);
		convert = convert->base;
	}
	else
		output->expr = NULL;

	// TODO: Allow multi-level arrays
	if(convert->mode == TYPE_ARRAY)
	{
		fprintf(stderr, "Multi-level arrays are currently not supported in HWC.\n");
		assert(0);
	}

	// Note: We don't set *base_plugType or *base_part yet. Set type so we can check their validity later.
	//   We could check for and set decls of type "bit" here, but we'll need to check the part/plug name
	//   later anyhow, so pass on it for now
	output->type     = convert->mode;
	output->typeName = convert->ident;

	output->isMem    = input->isMem;

	output->base_plugType = NULL;
	output->base_part     = NULL;

	// Temp dummy value that might be useful later
	output->index = -1;
}


/*
TODO: Add actually good header comment
	isWithinPlug is used to check whether all the decls inside a plugtype is another plugtype
		if 1 is plug
		if 0 is not
	Retval: 0 if no errors, 1 if errors
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
			// TODO: Add default plugtype 'bit'
			fprintf(stderr, "TODO: Add BIT!\n");
			assert(0);
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

			// Check to make sure a Part declaration isn't inside a plugtype
			if(isWithinPlug == 1 && currName->part != NULL)
			{
				fprintf(stderr, "Part declaration inside a plugtype!\n");
				assert(0);
			}

			if(currName->part != NULL)
				currDecl->base_part     = currName->part;
			else
				currDecl->base_plugType = currName->plugtype;

			break;
	}
	return 0;
}
