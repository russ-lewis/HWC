#ifndef __SEMANTIC_NAMES_H__INCLUDED__
#define __SEMANTIC_NAMES_H__INCLUDED__


/* Name Scope
 *
 * The names which are available at any given location are organized into a
 * chain of 'scope' objects.  The outermost scope is import scope; in this,
 * each of the imported files shows up a single name.  (Technically, it's
 * represented as a *tree* of objects, since the import names are
 * period-delimited.  But the concept remains.)
 *
 * NOTE: import scope is TBD for the future - for now
 *
 * Below the import scope is the file declaration scope, which lists all of
 * the names declared inside the file, including parts, plugtypes, and any
 * compile-time variables.
 *
 * NOTE: global compile-time variables are TBD for the future - for now
 *
 * Inside each part or plugtype is another scope, which lists all of the
 * fields or plugs declared in that type.
 *
 * Inside if() and for() statemens (but *NOT* static-if()), there is another
 * name scope, which gives the (private) plugs, compile-time variables, and
 * parts which are only visible inside this statement.  These statement
 * scopes can be nested arbitrarily deep (unlike all of the other types).
 *
 * ---
 *
 * As we go through the sematic phase of the compiler, we will build up each
 * of the scopes; we will add names to them as we see new declarations.  As
 * we reach the end of a given block (file, part, plugtype, or statement),
 * we will either save the pointer to this name scope into the object we've
 * created (for later lookup), or else we will free the name scope object.
 *
 * ---
 *
 * Searching for a name involves searching through each of the scopes in
 * turn, starting at the deepest one and moving toward the "parent" scopes
 * further out.  A search will either return NULL (name not found), or else
 * a pointer to a nameable object.
 *
 * ---
 *
 * Duplicate and overlapping names are never allowed - so, any time that we
 * attempt to add a name to a scope, we will first confirm that the name does
 * not exist in that scope, or any enclosing scope.
 */

/* IMPLEMENTATION
 *
 * We are implementing this as a quasi-class.  Implementation is entirely
 * hidden from the caller (and is likely to change when we have time to write
 * better code).  Callers are responsible for using incRef() and decRef() to
 * track how many times a given name scope is referenced; the code will
 * do reference counting and garbage-collect any scope which is no longer in
 * use.  (malloc() implicitly sets a refcount of 1 before it returns the
 * newly-created object.)
 */


typedef struct HWC_NameScope HWC_NameScope;
typedef struct HWC_Nameable  HWC_Nameable;


HWC_NameScope *nameScope_malloc(HWC_NameScope *parent);

void nameScope_incRef(HWC_NameScope *obj);
void nameScope_decRef(HWC_NameScope *obj);

HWC_Nameable *nameScope_search(HWC_NameScope *obj, char *name);
void          nameScope_add   (HWC_NameScope *obj, char *name, HWC_Nameable *thing);



typedef struct HWC_File     HWC_File;
typedef struct HWC_Part     HWC_Part;
typedef struct HWC_PlugType HWC_PlugType;
typedef struct HWC_Type     HWC_Type;
typedef struct HWC_Plug     HWC_Plug;

struct HWC_Nameable
{
	HWC_File     *file;
	HWC_Part     *part;
	HWC_PlugType *plugtype;
	HWC_Type     *type;
	HWC_Plug     *plug;
};



/* HACK
 *
 * Since compile.c violates the encapsulation, we moved the struct definition
 * into the header.  We'll move it back into the .c file if we later
 * re-enforce the encapsulation.
 */
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



void nameScope_dump(HWC_NameScope*, int prefixLen);


#endif

