#include <stdio.h>
#include <assert.h>

#include "parser.tab.h"
#include "pt/all.h"
#include "semantic/phase1.h"
#include "semantic/phase4.h"
#include "wiring/build.h"


// global, shared with the parser, through parsercommon.h
PT_file *bisonParseRoot;



int main()
{
	int parseRetval = yyparse();
	printf("yyparse() retval: %d\n", parseRetval);
	if (parseRetval != 0)
		return parseRetval;

	printf("\n");
	printf("---- DEBUG OUTPUT BEGINS ----\n");
	printf("\n");

	dump_file(bisonParseRoot, 0);

	printf("\n");
	printf("---- DEBUG OUTPUT ENDS, SEMANTIC PHASE BEGINS ----\n");
	printf("\n");


	/* phase 1 happens linearly across the entire file (it is not
	 * recursive).  It simply parses the list of declarations in the file
	 * into a NameScope object, as well as doing first-step transformation
	 * of the parse tree into the local format.
	 */
	HWC_NameScope *fileScope = semPhase1_file(bisonParseRoot);


	/* the next three phases are recursive (types depending on types),
	 * and sometimes there are complex relationships.  So, what we do here
	 * is to iterate through the declarations inside the file, and ask
	 * each one to perform the Semantic Phase 4.  Each Phase 4 call will
	 * iterate through phases 2,3,4 in order; each of these will recurse
	 * as necessary into other types (at the required phase).  Since
	 * the recursive operations will require us to run some of the early
	 * phases on some types before we actually get there in the iteration
	 * through the file; we will notice this, and the later calls will
	 * become NOPs.
	 */

	/* HACK
	 *
	 * Since this is the only place where we need to iterate through the
	 * names in a file, so we have imported in-depth knowledge of the
	 * NameScope design here.  This breaks encapsulation, but it's easier
	 * and cleaner code than doing the complexity of implementing a
	 * proper iterator type.  This means, of course, that we will have to
	 * update this code if/when we update the NameScope data structure,
	 * that's only one copy to change, and it would be the same if we had
	 * an iterator.
	 *
	 * Later, if we need iteration in another place, we might port this
	 * to use a good encapsulated design.  But not now.
	 */
	assert(fileScope->parent == NULL);

	HWC_NameScope_elem *cur = fileScope->list;
	while (cur != NULL)
	{
		assert((cur->thing->part     != NULL) !=
		       (cur->thing->plugtype != NULL));

		if (cur->thing->part != NULL)
			semPhase4_part(cur->thing->part);
		else
			semPhase4_plugtype(cur->thing->plugtype);

		cur = cur->next;
	}


	/* look up the name 'main'.  If it doesn't exist, then report an
	 * error to the user.  If it's not a part, then also report an error.
	 */
	HWC_Nameable *thing = nameScope_search(fileScope, "main");

	if (thing == NULL)
		assert(0);   // report erorr to user
	if (thing->part == NULL)
		assert(0);   // report erorr to user


	/* build the wiring diagram! */
	HWC_Wiring *wiring = buildWiringDiagram(thing->part);

	return 0;
}

