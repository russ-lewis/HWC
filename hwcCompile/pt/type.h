#ifndef __PARSE_TREE__TYPE_H__INCLUDED__
#define __PARSE_TREE__TYPE_H__INCLUDED__


typedef struct PT_type PT_type;

typedef struct PT_expr PT_expr;

enum {
	TYPE_BIT = 1,
	TYPE_ARRAY,
	TYPE_IDENT,
};

struct PT_type
{
	/* choose from the enum above */
	int mode;

	/* TYPE_BIT - no fields */

	/* TYPE_ARRAY */
	PT_type *base;
	PT_expr *len;

	/* TYPE_IDENT */
	char	  *ident;
};


void dump_pt_type(PT_type *obj, int spaces);


#endif

