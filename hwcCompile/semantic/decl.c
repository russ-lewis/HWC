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

	output->base_plugType = NULL;
	output->base_part     = NULL;

	// Temp dummy value that might be useful later
	output->index = -1;
}
