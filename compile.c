#include <stdio.h>

#include "parser.tab.h"
#include "pt/all.h"
#include "semantic/phase1.h"

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

	HWC_NameScope *fileScope = semPhase1_file(bisonParseRoot);

	return 0;
}

