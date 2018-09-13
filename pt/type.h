#ifndef __PARSE_TREE__TYPE_H__INCLUDED__
#define __PARSE_TREE__TYPE_H__INCLUDED__


typedef struct PT_type PT_type;


enum {
	TYPE_BIT = 1,
	TYPE_ARRAY,
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


#endif

