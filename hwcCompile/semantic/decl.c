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

	assert(0);
	// Note: We don't set *base_plugType or *base_part yet. Set type so we can check their validity later.
	//   We could check for and set decls of type "bit" here, but we'll need to check the part/plug name
	//   later anyhow, so
	// TODO: SHOULD WE BE CONVERTING PT_TYPE TO A HWC_TYPE INSTEAD?

	// TODO: IF CONVERT->MODE == TYPE_ARRAY, WHAT TO DO WITH CONVERT->LEN? WE ALREADY USE ARRAYSUFFIX BELOW
	PT_type *convert = input->type;
	if(convert->mode == TYPE_ARRAY)
		convert = convert->base;

	output->type     = convert->mode;
	output->typeName = convert->ident;

	output->base_plugType = NULL;
	output->base_part     = NULL;

	// TODO: Below is a copy of the PT_array_decl struct, which is where we get the expr for this decl from
	//       How should we accout for arraySuffix->prev being valid?
	/*
	struct PT_array_decl
	{
		PT_array_decl *prev;

		PT_expr *size;
	};
	*/
	if(input->arraySuffix == NULL)
		output->expr = NULL;
	else
		convertPTexprIntoHWCexpr(input->arraySuffix->size, output->expr);

	// Temp dummy value that might be useful later
	output->index = -1; // TODO: Is this necessary?
}
