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
	/* run the parser.  Then collect the root object from Bison */
	int parseRetval = yyparse();
	if (parseRetval != 0)
		return parseRetval;

	HWC_Wiring *core = bisonParseRoot;
	assert(core != NULL);

	// TODO: add debug switches... wiring_write(core);

	assert(0);   // TODO
}

