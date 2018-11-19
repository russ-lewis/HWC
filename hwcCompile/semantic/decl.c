
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
	// TODO: What to put for these vars? Comment copied below.
	/* In a Decl that is part of a PlugType, we know for *sure* that
	 * the base type of the Decl is another PlugType.  In a Part, there
	 * can be some Decl's that refer to PlugType's (the various plugs of
	 * the Part), and others that refer to Part's (the various
	 * subcomponents).
	 *
	 * NOTE: We do not need to remember public/private in this struct,
	 *       because that information is implicitly stored - it simply
	 *       tells us which NameScope(s) will contain the name for this
	 *       Decl.
	 */
	//HWC_PlugType *base_plugType;
	//HWC_Part     *base_part;

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

	/*
	struct PT_decl
	{
   //linked list, in reverse order of declaration
   PT_decl *prev;

   PT_type *type;
   char *name;
   PT_array_decl *arraySuffix;
	};
	*/
}
