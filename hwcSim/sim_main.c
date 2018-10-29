#include <stdio.h>
#include <string.h>
#include <assert.h>

#include "parser.tab.h"
#include "wiring/core.h"
#include "wiring/write.h"


// global, shared with the parser, through parsercommon.h
HWC_Wiring *bisonParseRoot;



int main(int argc, char **argv)
{
	/* parse the command-line arguments.  TODO: make use of getopt() */

	int debug = 0;   // if nonzero, is the place to "stop and dump state"
	int syntaxHelp = 0;

	if (argc == 2 && strcmp(argv[1], "--debug=parse") == 0)
		debug = 1;
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
		return 0;
	}


	/* run the parser.  Then collect the root object from Bison */
	int parseRetval = yyparse();
	if (parseRetval != 0)
		return parseRetval;

	HWC_Wiring *core = bisonParseRoot;
	assert(core != NULL);

	/* dump debug state, if requested */
	if (debug == 1)
	{
		wiring_write(core);
		return 0;
	}


	assert(0);   // TODO
}

