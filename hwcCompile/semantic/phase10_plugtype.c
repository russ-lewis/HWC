#include <stdio.h>
#include <malloc.h>
#include <memory.h>

#include <assert.h>

#include "phase10.h"

/*
TODO: Header comment
TODO: Should we remove *fileScope argument? On one hand, it isn't used. On the other, it could be useful one day and it mirrors semPhase10_part.
*/
HWC_PlugType *semPhase10_plugtype(PT_plugtype_decl *parsedPlugtype,
                                 HWC_NameScope    *fileScope)
{
	assert(0);    // TODO

#if 0
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
	HWC_PlugType *retval = malloc(sizeof(HWC_PlugType));
	if (retval == NULL)
	{
		assert(0);   // TODO: debug message
		return NULL;
	}
	memset(retval, 0, sizeof(*retval));

	retval->phases_completed = retval->phases_begun = 10;

	// Create publicNames, and make "NULL" its parent
	retval->publicNames = nameScope_malloc(NULL);
	if (retval->publicNames == NULL)
	{
		assert(0);   // TODO: debug message
		free(retval);
		return NULL;
	}
	// PlugTypes have no private fields, so only create a public nameScope

	HWC_Decl *decl_list_head = NULL;
	// Implementation can be found in stmts.c
	// Creates an ordered (? Not necessary) list of decls within this part.
	retval->decls_len = extractHWCdeclsFromPTstmts(parsedPlugtype->stmts, decl_list_head, retval->publicNames, NULL);

	return retval;
}
