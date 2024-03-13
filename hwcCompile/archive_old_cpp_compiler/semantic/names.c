
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <assert.h>

#include "names.h"



/* HWC_NameSCope is not declared in the header.  Its implementation is
 * private.
 *
 * On the other hand, this file does *NOT* give the declaration for
 * HWC_Nameable, since that struct is opaque to this code.  Currently (as of
 * 25 Sep 2018), the latter struct is defined in names.h, as it is intended as
 * a "dumb" struct (no methods).  If that changes, the declaration might be
 * moved inside some other C file.  But either way, there's no need to have it
 * here.
 */

/* UPDATE: we moved this into the header because compile.c breaks the
 *         encapsulation.  We'll move the struct back here if we later
 *         change the design to obey the encapsulation.
 */
#if 0
typedef struct HWC_NameScope_elem HWC_NameScope_elem;
struct HWC_NameScope
{
	// we'll auto-free() when this goes to zero
	int refCount;

	// this is the enclosing scope
	HWC_NameScope *parent;

	/* TODO: replace this linked list with a more efficient data
	 *       structure.  How about a binary tree, with empty subtrees
	 *       pointing directly to subtrees in the parent, would that
	 *       work???
	 */
	HWC_NameScope_elem *list;
};

struct HWC_NameScope_elem
{
	char         *name;
	HWC_Nameable *thing;

	HWC_NameScope_elem *next;
};
#endif



HWC_NameScope *nameScope_malloc(HWC_NameScope *parent)
{
	HWC_NameScope *retval = malloc(sizeof(HWC_NameScope));
	  assert(retval != NULL);
		// TODO: better error reporting

	retval->refCount = 1;
	retval->parent   = parent;
	retval->list     = NULL;

	return retval;
}



void nameScope_incRef(HWC_NameScope *obj)
{
	assert(obj != NULL);
	obj->refCount++;
}

void nameScope_decRef(HWC_NameScope *obj)
{
	assert(obj != NULL);
	assert(obj->refCount > 0);

	obj->refCount--;

	if (obj->refCount == 0)
	{
		assert(0);  // TODO: implement me
	}
}



#define SEARCH_DEBUG 0
HWC_Nameable *nameScope_search(HWC_NameScope *obj, char *name)
{
	assert(obj != NULL);

	if (SEARCH_DEBUG)
		printf("--- BEGIN %s(%p, '%s')\n", __func__, obj,name);

	HWC_NameScope_elem *cur = obj->list;
	while (cur != NULL)
	{
		if (SEARCH_DEBUG)
			printf("cur->name='%s' name='%s'\n", cur->name,name);

		if (strcmp(cur->name, name) == 0)
			return cur->thing;
		cur = cur->next;
	}

	if (SEARCH_DEBUG)
		printf("obj->parent=%p\n", obj->parent);

	if (obj->parent == NULL)
		return NULL;
	return nameScope_search(obj->parent, name);
}

/*
Associates "name" with "thing" inside the given nameScope "obj"
*/
void nameScope_add(HWC_NameScope *obj, char *name, HWC_Nameable *thing)
{
	assert(obj != NULL);
	assert(nameScope_search(obj,name) == NULL);
	assert(name != NULL);
	assert(strlen(name) != 0);   // TODO: add name-sanity-checking
	assert(thing != NULL);

	assert(thing->fr.filename != NULL);

	/* find the pointer-to-tail */
	HWC_NameScope_elem **pPtr = &obj->list;
	HWC_NameScope_elem  *cur  = *pPtr;

	while (cur != NULL)
	{
		pPtr = &cur->next;
		cur  = *pPtr;
	}

	cur = malloc(sizeof(HWC_NameScope_elem));
	  assert(cur != NULL);  // TODO: better error checking

	cur->name  = name;
	cur->thing = thing;
	cur->next  = NULL;

	*pPtr = cur;
	return;
}


