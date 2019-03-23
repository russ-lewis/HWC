#ifndef __SEMANTIC_PHASE10_H__INCLUDED__
#define __SEMANTIC_PHASE10_H__INCLUDED__


/* SEMANTIC PHASE 10
 *
 * This declares the functions that are used to perform "phase 10" of the
 * semantic work for HWC: this converts the parse tree into a set of
 * internal HWC objects; this phase focuses on name resolution.
 */

#include "pt/all.h"

#include "semantic/names.h"

#include "semantic/part.h"
#include "semantic/plugtype.h"
#include "semantic/stmt.h"
#include "semantic/expr.h"



/* This takes a parse-tree at the file level as input, and returns a
 * newly-created NameScope object for that file.  Inside that NameScope are
 * pointers to the various declarations inside the file; these allow you to
 * find the HWC_Part, HWC_PlugType, etc. pointers.
 *
 * Note that this function does *NOT* create an HWC_File object; that is
 * something which you can create to *contain* this NameScope (when/if that
 * is necessary).
 *
 * Also, note that you will be passed an object with a single refCount; if
 * you discard this NameScope, then you must decrement the refcount on it.
 */
HWC_NameScope *semPhase10_file(PT_file *parsedFile);



/* ------- HELPER FUNCTIONS FOR THE ABOVE -------
 * All of the rest of the functions below are helpers for the main function
 * above.  That is, main() will call the above, and it will recurse down
 * through the structures of the parse tree, building the various semantic
 * structures.
 *
 * The new structure that we build will (more or less) mirror the parse tree,
 * except that linked lists will be converted into arrays.  Also, decl
 * statements will be inlined into the statement arrays (in the semantic
 * phase, each statement can only contain a single declaration).
 *
 * There are a couple of query functions, which simply return int; these are
 * used to count the number of elements in a list, so that we can allocate
 * arrays.
 *
 * However, most of the logic in this phase is made up of objects that
 * convert parse tree structures into semantic structures.  These functions
 * use three different types of return values, depending on the operation
 * which must be performed: 
 *
 *     - malloc() a struct and return it (like phase10_file() above); return
 *       NULL on error. 
 *
 *     - Take two pointer parameters, an input and output.  The output must
 *       be allocated by the caller (often, as part of an array of such
 *       objects).  Returns 0 on success, nonzero on error. 
 *
 *     - Take an input parameter, which points to the parse tree, and two
 *       output parameters: a pointer to an array variable, and a pointer
 *       to an integer.  Count the size of the parse tree, allocate an
 *       array, fill the array, and store the array pointer and the length
 *       using the output parameters.  Returns 0 on success, nonzero on
 *       error.
 *
 * In addition to the parameters mentioned above, many functions will also
 * take secondary paramters, which are important for the conversion
 * process.
 */


/* these build entire parts or plugtypes.  They return newly-malloc()ed
 * objects.  Each has a secondary parameter, which is the current
 * file-level name scope.
 */

HWC_Part     *semPhase10_part    (PT_part_decl     *parsedPart,
                                  HWC_NameScope *fileScope);
HWC_PlugType *semPhase10_plugtype(PT_plugtype_decl *parsedPlugtype,
                                  HWC_NameScope *fileScope);


/* this counts the number of statements in a linked list; declarations are
 * inlined into the count, because each semantic statement can hold only
 * a *single* declaration.
 *
 * This function is *NOT* recursive; BLOCK, IF, and FOR statements each
 * show up as a single statement in this count (we will recurse when
 * *building* the statements, and build smaller arrays to represent the
 * nested statements).
 *
 * The input may be NULL; returns 0 in that case.
 *
 * Returns a count (which might be zero).  Never reports any error.
 */
int countStmtsInPT(PT_stmt *stmtList);


/* this converts an entire list of statements from the parse tree into
 * an array of semantic statements.  Declarations are inlined as noted
 * previously.
 *
 * This function *does* recurse; when converting a BLOCK, IF, or FOR
 * statement, we will completely build all of the nested statements.
 *
 * This function will malloc() an array of semantic statements.  If
 * the input was NULL (meaning no statements), then it will allocate
 * an array with a single STMT_NOP statement.
 *
 * The input is a pointer to the statement list.  It also has two
 * output parameters, where we store the pointer to the allocated
 * array, and its length.
 *
 * The function also includes two name parameters (public and private);
 * the private may be NULL (in the case of statements inside of a plugtype),
 * but the public must never be NULL.
 *
 * This returns 0 on success, nonzero on error.  This function will be
 * responsible for printing out any error message associated with any error;
 * the caller is not expected to print *anything*.
 */
int phase10_stmtList(PT_stmt   *stmtList,
                     HWC_Stmt **arr_out, int arrLen_out,
                     HWC_NameScope *publicNames, HWC_NameScope *privateNames);


/* these helper functions convert a single PT declaration or statement
 * into a pre-allocated statement object.  The caller is expected to memset()
 * the struct, and set up the FileRange, mode, and name scopes before making
 * these calls.
 *
 * These functions return 0 on success, nonzero on error.  As above, these
 * functions will print out any error messages required.
 *
 * DECL: This is weird, because we are inlining the declarations into the
 *       statements.  We call _common() on the first statement in the
 *       inlined set - this fills in the common fields about the declaration
 *       (type, memory, public, etc.).  Then the _one() call is called on
 *       each name in the list, passing it a pointer to the common struct
 *       (which, in the case of the first decl, is the *same* object).  This
 *       will set up the the per-declaration fields.
 */
int phase10_stmt_DECL_common(PT_stmt *declStmt,
                             HWC_Stmt *output);
int phase10_stmt_DECL_on(PT_decl  *declName,
                         HWC_Stmt *output, HWC_Stmt *firstOfList);

int phase10_stmt_CONN  (PT_stmt *input, HWC_Stmt *output);
int phase10_stmt_IF    (PT_stmt *input, HWC_Stmt *output);
int phase10_stmt_FOR   (PT_stmt *input, HWC_Stmt *output);
int phase10_stmt_BLOCK (PT_stmt *input, HWC_Stmt *output);
int phase10_stmt_ASSERT(PT_stmt *input, HWC_Stmt *output);


/* this helper function converts a parse tree expression into a semantic
 * expression.  This returns the newly-created object on success, or NULL
 * on failure.
 *
 * We pass the private names for this context as a parameter, we do *NOT*
 * attempt to resolve any names yet (this happens in phase 20), but we
 * save the NameScope pointers for later use in that phase.
 */
HWC_Expr *phase10_expr(PT_expr *input, HWC_NameScope *privateNames);



#endif

