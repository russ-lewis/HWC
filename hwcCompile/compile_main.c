#include <stdio.h>
#include <string.h>
#include <getopt.h>
#include <assert.h>

#include "parser.tab.h"
#include "pt/all.h"
#include "semantic/phase10.h"
#include "semantic/phase20.h"
#include "semantic/phase30.h"
#include "semantic/phase40.h"
#include "wiring/build.h"
#include "wiring/write.h"


// globals, shared with the parser, through parsercommon.h
PT_file *bisonParseRoot;
char    *bisonParse_filename;



int main(int argc, char **argv)
{
	char *outfile = NULL;
	int debug = 0;   // if nonzero, is the place to "stop and dump state"


	/* example code: https://www.gnu.org/software/libc/manual/html_node/Getopt-Long-Options.html#Getopt-Long-Options */

	struct option options[] = {
            { "o",     required_argument, NULL, 'o' },
            { "debug", required_argument, NULL, 'd' },
            { 0,0,0,0 }
	};

	int opt;
	while ((opt = getopt_long(argc, argv, "o:", options, NULL)) != -1)
	{
		switch (opt)
		{
		case 'o':
			outfile = optarg;
			break;

		case 'd':
			if (strcmp(optarg, "parse") == 0)
			{
				debug = 1;
				break;     // do *NOT* fallthrough
			}
			if (strcmp(optarg, "semantic_phase10") == 0)
			{
				debug = 2;
				break;     // do *NOT* fallthrough
			}
			if (strcmp(optarg, "semantic_phase20") == 0)
			{
				debug = 3;
				break;     // do *NOT* fallthrough
			}
			if (strcmp(optarg, "semantic_phase30") == 0)
			{
				debug = 4;
				break;     // do *NOT* fallthrough
			}
			if (strcmp(optarg, "semantic_phase40") == 0)
			{
				debug = 5;
				break;     // do *NOT* fallthrough
			}
			else
			{
				fprintf(stderr, "ERROR: The only supported debug modes are 'parse', 'semantic_phase10', 'semantic_phase20', 'semantic_phase30', 'semantic_phase40'\n");
				// intentional fallthrough
			}

		case '?':
			fprintf(stderr, "SYNTAX: %s [--debug=MODE] [-o <outfile>]\n", argv[0]);
			fprintf(stderr, "  debug MODEs:\n");
			fprintf(stderr, "    parse\n");
			fprintf(stderr, "    semantic_phase10\n");
			fprintf(stderr, "    semantic_phase40\n");
			return 1;
		}
	}


	/* TODO: turn this into a command line argument, so that we will get
	 *       nice filenames in the wiring diagrams.
	 */
	bisonParse_filename = "<stdin>";


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

		int retval;
		if (debug == 3)
		{
			if (cur->thing->part != NULL)
				retval = semPhase20_part(cur->thing->part);
			else
				retval = semPhase20_plugtype(cur->thing->plugtype);
		}
		else if (debug == 4)
		{
			if (cur->thing->part != NULL)
				retval = semPhase30_part(cur->thing->part);
			else
				retval = semPhase30_plugtype(cur->thing->plugtype);
		}
		else
		{
			if (cur->thing->part != NULL)
				retval = semPhase40_part(cur->thing->part);
			else
				retval = semPhase40_plugtype(cur->thing->plugtype);
		}

		if (retval != 0)
			return retval;

		cur = cur->next;
	}

	/* shall we "stop and dump state" for the semantic phase? */
	if (debug == 3 || debug == 4 || debug == 5)
	{
		if (debug == 3)
			printf("---- DEBUG: DUMPING SEMANTIC (after phase 20) ----\n");
		if (debug == 4)
			printf("---- DEBUG: DUMPING SEMANTIC (after phase 30) ----\n");
		if (debug == 5)
			printf("---- DEBUG: DUMPING SEMANTIC (after phase 40) ----\n");

		nameScope_dump(fileScope, 0);
		return 0;
	}


	/* look up the name 'main'.  If it doesn't exist, then report an
	 * error to the user.  If it's not a part, then also report an error.
	 */
	HWC_Nameable *thing = nameScope_search(fileScope, "main");

	if (thing == NULL)
	{
		fprintf(stderr, "%s: File does not include a type 'main', cannot compile.\n", bisonParse_filename);
		return 1;
	}
	if (thing->part == NULL)
	{
		fprintf(stderr, "%s: 'main' is not a part declaration, cannot compile.\n", bisonParse_filename);
		return 1;
	}


	/* build the wiring diagram! */
	HWC_Wiring *wiring = buildWiringDiagram(thing->part);
	if (wiring == NULL)
		return 1;   // the wiring generator must have already printed an error message


	if (outfile == NULL)
	{
		fprintf(stderr, "ERROR: No outfile specified.  Please use -o <file>.\n");
		fprintf(stderr, "TODO: make this automatic, based on the infile name.\n");
		return 1;
	}


	FILE *out = fopen(outfile, "w");
	int rc = wiring_write(wiring, out);
	fclose(out);
	return rc;
}

