#ifndef __SEMANTIC_DECL_H__INCLUDED__
#define __SEMANTIC_DECL_H__INCLUDED__

/* This struct represents a declaration, as represented in the semantic
 * phase.  Each of these declarations is inside of a PT_stmt in the parse
 * tree, but will be extracted, early in the semantic phase, into an array
 * of structs, stored directly in the PlugType or Part.
 *
 * Since we will never need to know the name of any declaration *AFTER* we
 * have found it (since we always find it by name), we don't need to store
 * the name here; it is implicitly encoded as pointers, stored in one or
 * more NameScope objects.
 *
 * The information that this must carry are:
 *     - The base type of the declared name, which is a pointer to a
 *       PlugType or Part;
 *     - The array metadata (since the base types will never be array types)
 *     - The index where the bits of this declared name begin, inside the
 *       enclosing PlugType or Part.
 */
#include <pt/stmt.h>
#include <pt/part.h> // Need for PT_array_decl
#include <pt/type.h>
#include "expr.h"

typedef struct HWC_Expr HWC_Expr;
typedef struct HWC_PlugType HWC_PlugType;
typedef struct HWC_Part HWC_Part;

typedef struct HWC_Decl HWC_Decl;
struct HWC_Decl
{

	/*
	"typeName" is useful in phase10 because we are populating the namescope with the names of decls,
	  but we can't check for the existence of parts/plugtypes outside of our own.
	Once we know whether the type of a name is valid, "typeName" becomes useless and base_p* below
	  stores the relevant type that this decl is an instantiation of.
	Example: [PartName  partInstance;]
	          ^typeName ^stored implicitly in nameScope
	*/
	char *typeName;

	/* In a Decl that is part of a PlugType, we know for *sure* that
	 * the base type of the Decl is another PlugType.  In a Part, there
	 * can be some Decl's that refer to PlugType's (the various plugs of
	 * the Part), and others that refer to Part's (the various
	 * subcomponents).
	 *
	 * NOTE: We do not need to remember public/private in this struct,
	 *       because that information is implicitly stored - it simply
	 *       tells us which NameScope(s) will contain the name for this
	 *       Decl.
	 */
	HWC_PlugType *base_plugType;
	HWC_Part     *base_part;


	/* array size.  This is a single expression if the Decl is an array;
	 * we will validate, near the end of the semantic phase, that it is
	 * of type INT and that it has a non-negative value.
	 *
	 * If this is NULL, then this Decl is not an array.
	 *
	 * TODO: support multidimensional arrays in the future.
	 */
	HWC_Expr *expr;


	/* bit index of this Decl inside its enclosing PlugType or Part */
	int index;
};

void convertPTdeclIntoHWCdecl(PT_decl *, HWC_Decl *);

#endif

