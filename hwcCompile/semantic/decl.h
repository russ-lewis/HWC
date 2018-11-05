#ifndef __SEMANTIC_DECL_H__INCLUDED__
#define __SEMANTIC_DECL_H__INCLUDED__


#include <pt/stmt.h>    // we'll re-use the modes from the parser

typedef struct HWC_Decl HWC_Decl;
struct HWC_Decl
{
	char     *name
	HWC_Type *type;
	HWC_Expr *expr;
};

struct PT_decl
{
	/* linked list, in reverse order of declaration */
	PT_decl *prev;

	PT_type *type;
	char *name;
	PT_array_decl *arraySuffix;
};


int convert PTdeclIntoHWCdecl(PT_Decl *, HWC_Decl *);

#endif

