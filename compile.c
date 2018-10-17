#include <stdio.h>
#include <string.h>

#include "parser.tab.h"
#include "pt/all.h"
#include "semantic/phase1.h"

// global, shared with the parser, through parsercommon.h
PT_file *bisonParseRoot;



int main(int argc, char **argv)
{
	/* parse the command-line arguments.  TODO: make use of getopt() */

	int debug = 0;   // if nonzero, is the place to "stop and dump state"
	int syntaxHelp = 0;

	if (argc == 2 && strcmp(argv[1], "--debug=parse") == 0)
		debug = 1;
	else if (argc == 2 && strcmp(argv[1], "--debug=semantic_phase1") == 0)
		debug = 2;
	else if (argc == 2 && strcmp(argv[1], "--debug=semantic_phase4") == 0)
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
		printf("    semantic_phase1\n");
		printf("    semantic_phase4\n");
		return 0;
	}


	/* run the parser.  Then collect the root object from Bison */
	int parseRetval = yyparse();
	printf("yyparse() retval: %d\n", parseRetval);
	if (parseRetval != 0)
		return parseRetval;

	/* shall we "stop and dump state" for the parse tree? */
	if (debug == 1)
	{
		printf("---- DEBUG: DUMPING PARSE TREE ----\n");
		dump_pt_file(bisonParseRoot, 0);
		return 0;
	}


	HWC_NameScope *fileScope = semPhase1_file(bisonParseRoot);

	/* shall we "stop and dump state" for the semantic phase? */
	if (debug == 2)
	{
		printf("---- DEBUG: DUMPING SEMANTIC (after phase 1) ----\n");
		nameScope_dump(fileScope, 0);
		return 0;
	}


	printf("TODO: implement semantic phase 4\n");
	return 0;
}

