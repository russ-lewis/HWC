#ifndef __SEMANTIC_DECL_H__INCLUDED__
#define __SEMANTIC_DECL_H__INCLUDED__


#include <pt/stmt.h>    // we'll re-use the modes from the parser



/* this part is used to store the parse tree for the nonterminals
 * 'field', as well as its sub-nonterminals field_decls, etc.  Each
 * of these instances represents 
 *
 * This nonterminal is used in two places:
 *    - PlugTypes are entirely made up of nothing other than this;
 *      
 */
struct PT_decl
{
	/* linked list, in reverse order of declaration */
	PT_decl *prev;

	PT_type *type;
	char *name;
	PT_array_decl *arraySuffix;
};


/* TODO */
typedef struct HWC_Decl HWC_Decl;
struct HWC_Decl
{
	char     *name
	HWC_Type *type;

	/* this is the size of the array.  If this is NULL, then this *NOT*
	 * an array, it's a simple instiation of the PlugType
	 */
	HWC_Expr *expr;
};

int convert PTdeclIntoHWCdecl(PT_Decl *, HWC_Decl *);

#endif

