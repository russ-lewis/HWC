#ifndef __PARSE_TREE__TYPE_H__INCLUDED__
#define __PARSE_TREE__TYPE_H__INCLUDED__

#include "debug.h"

typedef struct PT_type PT_type;


enum {
	TYPE_BIT = 1,
	TYPE_ARRAY = 2,
};

struct PT_type
{
	/* choose from the enum above */
	int mode;

	/* TYPE_BIT - no fields */

	/* TYPE_ARRAY */
	PT_type *base;
	char        *len;
};


static void dump_type(PT_type *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1) 
		return;

	switch (obj->mode)
	{
	default:
		printf("-- debug: UNRECOGNIZED TYPE ---\n");
		break;

	case TYPE_BIT:
		printf("type: BIT\n");
		break;

	case TYPE_ARRAY:
		printf("type: ARRAY\n");          // line 1

		dump_type(obj->base, spaces+2);   // line 2

		dump_helper(obj,spaces);
		printf("len = %s\n", obj->len);   // line 3
		break;
	}
}


#endif

