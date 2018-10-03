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

	PT_file *file = bisonParseRoot;

	printf("file                      = %p\n", file);                        fflush(NULL);
	printf("file->decls               = %p\n", file->decls);                 fflush(NULL);
	printf("file->decls->    partDecl = %p\n", file->decls->    partDecl);   fflush(NULL);
	printf("file->decls->plugtypeDecl = %p\n", file->decls->plugtypeDecl);   fflush(NULL);
	printf("file->decls->prev         = %p\n", file->decls->prev);           fflush(NULL);

	printf("---- DEBUG OUTPUT BEGINS ----\n");
	dump_file(file, 0);
	printf("---- DEBUG OUTPUT ENDS ----\n");

	return 0;
}

