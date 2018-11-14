
#include <stdio.h>
#include <malloc.h>
#include <assert.h>

#include "phase10.h"


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

	// Implementation can be found in stmts.c
	//retval->stmts_len = convertPTstmtIntoHWCstmt(parsedPart->stmts, retval->stmts, retval);
}

