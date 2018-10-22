
#include <stdio.h>
#include <malloc.h>
#include <assert.h>

#include "phase10.h"


HWC_PlugType *semPhase10_plugtype(PT_plugtype_decl *parsedPlugtype,
                                 HWC_NameScope    *fileScope)
{
	assert(0);    // TODO

#if 0
	HWC_NameScope *names = nameScope_malloc(NULL);

	// should we traverse through the linked list in the correct order?
	// This version walks through them backwards (that is, it obeys the
	// structure of the structure of the list)

	PT_file_decl *cur = parsedFile->decls;
	while (cur != NULL)
	{
		assert((cur->partDecl != NULL) != (cur->plugtypeDecl != NULL));

		char *name;
		HWC_Nameable *thing = malloc(sizeof(HWC_Nameable));
		  assert(thing != NULL);   // TODO: better error checking

		if (cur->partDecl != NULL)
		{
			name = cur->partDecl->name;

			thing->part = semPhase10_part(cur->partDecl);
			  assert(thing->part != NULL);
			thing->plugtype = NULL;
		}
		else if (cur->plugtypeDecl != NULL)
		{
			name = cur->plugtypeDecl->name;

			thing->part = NULL;
			thing->plugtype = semPhase10_plugtype(cur->plugtypeDecl);
			  assert(thing->plugtype != NULL);
		}

		if (nameScope_search(names, name) != NULL)
		{
			assert(0);   // TODO: report syntax error
		}

		nameScope_add(names, name,thing);
	}

	return names;
#endif
}

