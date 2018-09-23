#ifndef __PARSE_TREE__TYPE_H__INCLUDED__
#define __PARSE_TREE__TYPE_H__INCLUDED__


typedef struct PT_type PT_type;

static void dump_type(PT_type *, int spaces);

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
	if(obj == NULL)
		return;

   int i;
   for(i = 0; i < spaces; i++)
      printf(" ");
   printf("Type: mode = %d\n", obj->mode);
	// TODO: Add different printfs for different types
}


#endif

