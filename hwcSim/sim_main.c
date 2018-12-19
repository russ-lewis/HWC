#include <stdio.h>
#include <string.h>
#include <getopt.h>
#include <assert.h>

#include "parser.tab.h"
#include "wiring/core.h"
#include "wiring/write.h"
#include "sim/graph2.h"


// global, shared with the parser, through parsercommon.h
HWC_Wiring *bisonParseRoot;



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
			else
			{
				fprintf(stderr, "ERROR: The only supported debug mode is 'parse'\n");
				// intentional fallthrough
			}

		case '?':
			fprintf(stderr, "SYNTAX: %s [--debug=MODE] [-o <outfile>]\n", argv[0]);
			fprintf(stderr, "  debug MODEs:\n");
			fprintf(stderr, "    parse\n");
			return 1;
		}
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
		wiring_write(core, outfile);
		return 0;
	}


	HWC_Sim_Graph *graph = HWC_Sim_buildGraph(core);


	assert(0);   // TODO
}

