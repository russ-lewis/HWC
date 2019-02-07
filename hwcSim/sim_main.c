#include <stdio.h>
#include <string.h>
#include <getopt.h>
#include <assert.h>

#include "wiring/parser.tab.h"
#include "wiring/core.h"
#include "wiring/write.h"
#include "sim/state.h"
#include "sim/tick.h"


// global, shared with the parser, through parsercommon.h
HWC_Wiring *bisonParseRoot;



// HACK!  Get rid of this global!
HWC_Sim_State *sim_global;



int main(int argc, char **argv)
{
#if 0
	char *outfile = NULL;
#endif

	int debug = 0;   // if nonzero, is the place to "stop and dump state"


	/* example code: https://www.gnu.org/software/libc/manual/html_node/Getopt-Long-Options.html#Getopt-Long-Options */

	struct option options[] = {
//            { "o",     required_argument, NULL, 'o' },
            { "debug", required_argument, NULL, 'd' },
            { 0,0,0,0 }
	};

	int opt;
	while ((opt = getopt_long(argc, argv, "o:", options, NULL)) != -1)
	{
		switch (opt)
		{
#if 0
		case 'o':
			outfile = optarg;
			break;
#endif

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
			// fprintf(stderr, "SYNTAX: %s [--debug=MODE] [-o <outfile>]\n", argv[0]);
			fprintf(stderr, "SYNTAX: %s [--debug=MODE]\n", argv[0]);
			fprintf(stderr, "  debug MODEs:\n");
			fprintf(stderr, "    parse\n");
			return 1;
		}
	}


	/* run the parser.  Then collect the root object from Bison */
	int parseRetval = yyparse();
	if (parseRetval != 0)
		return parseRetval;

	HWC_Wiring *wiring = bisonParseRoot;
	assert(wiring != NULL);

	/* dump debug state, if requested */
	if (debug == 1)
	{
		wiring_write(wiring, stdout);
		return 0;
	}


	HWC_Graph *graph = HWC_Graph_build(wiring);
	assert(graph != NULL);

	HWC_Sim_State *sim = HWC_Sim_buildState(graph);
	assert(sim != NULL);

	sim_global = sim;


	int limit = 10;   // eventually, this will be a command-line param

	int count = 0;
	while (count < limit)
	{
		HWC_Sim_doTick(sim);
		count++;
	}

	printf("SIMULATION TERMINATED.  sim ran for %d ticks.\n", count);
	return 0;
}

