
#include <stdio.h>
#include <malloc.h>
#include <assert.h>

#include "phase10.h"


HWC_NameScope *semPhase10_file(PT_file *parsedFile)
{
	// nameScope for the whole file
	HWC_NameScope *names = nameScope_malloc(NULL);

	// Should we traverse through the linked list in the correct order?
	// This version walks through them backwards (that is, it obeys the
	//   structure of the structure of the list)
	// FOLLOW-UP: It doesn't matter, because no part or plugtype cares
	//   about the namescope of the other types.
	//   So, order is arbitrary.

	PT_file_decl *cur = parsedFile->decls;
	// Iterate through all the parts and plugtypes in the file
	while (cur != NULL)
	{
		// Make sure "cur" is either a part or a plugtype, but not both
		assert((cur->partDecl != NULL) != (cur->plugtypeDecl != NULL));

		char *name;
		HWC_Nameable *thing = malloc(sizeof(HWC_Nameable));
		  assert(thing != NULL);   // TODO: better error checking

		// Get the name of the part/plug and run semPhase10 on it
		if (cur->partDecl != NULL)
		{
			fr_copy(&thing->fr, &cur->partDecl->fr);

			name = cur->partDecl->name;

			thing->part = semPhase10_part(cur->partDecl, names);
			  assert(thing->part != NULL);
			thing->plugtype = NULL;
		}
		else if (cur->plugtypeDecl != NULL)
		{
			fr_copy(&thing->fr, &cur->plugtypeDecl->fr);

			name = cur->plugtypeDecl->name;

			thing->part = NULL;
			thing->plugtype = semPhase10_plugtype(cur->plugtypeDecl, names);
			  assert(thing->plugtype != NULL);
		}

		// Removed because this assert already happens in add(), but I figured
		//   it should be preserved for example.
		/*
		if (nameScope_search(names, name) != NULL)
		{
			assert(0);   // TODO: report syntax error
		}
		*/

		// Add the part/plug (including its name) to the nameScope
		nameScope_add(names, name, thing);

		cur = cur->next;
	}

	return names;
}


