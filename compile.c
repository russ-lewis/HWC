#include <stdio.h>
#include <string.h>
#include <assert.h>

#include "parser.tab.h"
#include "pt/all.h"
#include "semantic/phase10.h"
#include "semantic/phase40.h"
#include "wiring/build.h"
#include "wiring/write.h"


// global, shared with the parser, through parsercommon.h
PT_file *bisonParseRoot;



int main(int argc, char **argv)
{
	/* parse the command-line arguments.  TODO: make use of getopt() */

	int debug = 0;   // if nonzero, is the place to "stop and dump state"
	int syntaxHelp = 0;

	if (argc == 2 && strcmp(argv[1], "--debug=parse") == 0)
		debug = 1;
	else if (argc == 2 && strcmp(argv[1], "--debug=semantic_phase10") == 0)
		debug = 2;
	else if (argc == 2 && strcmp(argv[1], "--debug=semantic_phase40") == 0)
		debug = 3;
	else if (argc == 2 && strcmp(argv[1], "-?") == 0)
		syntaxHelp = 1;
	else if (argc != 1)
	{
		fprintf(stderr, "ERROR: Invalid command line argument!\n");
		syntaxHelp = 1;
	}
	/* else NOP, the default state is just fine! */

	if (syntaxHelp)
	{
		printf("SYNTAX: %s [--debug=MODE]\n", argv[0]);
		printf("  debug MODEs:\n");
		printf("    parse\n");
		printf("    semantic_phase10\n");
		printf("    semantic_phase40\n");
		return 0;
	}


	/* run the parser.  Then collect the root object from Bison */
	int parseRetval = yyparse();
	if (parseRetval != 0)
		return parseRetval;

	/* shall we "stop and dump state" for the parse tree? */
	if (debug == 1)
	{
		printf("---- DEBUG: DUMPING PARSE TREE ----\n");
		dump_pt_file(bisonParseRoot, 0);
		return 0;
	}



	/* phase 1 happens linearly across the entire file (it is not
	 * recursive).  It simply parses the list of declarations in the file
	 * into a NameScope object, as well as doing first-step transformation
	 * of the parse tree into the local format.
	 */
	HWC_NameScope *fileScope = semPhase10_file(bisonParseRoot);

	/* shall we "stop and dump state" for the semantic phase? */
	if (debug == 2)
	{
		printf("---- DEBUG: DUMPING SEMANTIC (after phase 10) ----\n");
		nameScope_dump(fileScope, 0);
		return 0;
	}


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
			semPhase40_part(cur->thing->part);
		else
			semPhase40_plugtype(cur->thing->plugtype);

		cur = cur->next;
	}

	/* shall we "stop and dump state" for the semantic phase? */
	if (debug == 3)
	{
		printf("---- DEBUG: DUMPING SEMANTIC (after phase 40) ----\n");
		nameScope_dump(fileScope, 0);
		return 0;
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
	if (wiring == NULL)
		return 1;   // the wiring generator must have already printed an error message


	return wiring_write(wiring);
}

