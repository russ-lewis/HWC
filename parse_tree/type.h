#ifndef __PARSE_TREE__TYPE_H__INCLUDED__
#define __PARSE_TREE__TYPE_H__INCLUDED__


typedef struct Parser_Type Parser_Type;


enum {
	TYPE_BIT = 1,
	TYPE_ARRAY,
};

struct Parser_Type
{
	/* choose from the enum above */
	int opt;

	/* TYPE_BIT - no fields */

	/* TYPE_ARRAY */
	Parser_Type *base;
	char        *len;
};


#endif

