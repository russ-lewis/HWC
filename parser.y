/*
	A very rough parser for Hardware C
*/


/* Prologue C-statements */
%{
	#include <math.h>
	#include <stdio.h>
	#include <ctype.h>
	int yylex(void);
	void yyerror(char const *);

	// Allows for input and output to be in double
	#define YYSTYPE double
%}

/* Bison declarations */
%token PART
%token BIT
%token NUM
%token IDENT

/* Grammar Rules */
%%


/* Parses  */

/* Add a line type instead */

/* Plan for empty parts */
part:
		PART IDENT '{' part_stmts '}'
;

part_stmts:
		part_stmts part_stmt
	|	part_stmt
;

part_stmt:
		%empty				/* ie, there can be an empty lines within parts */
	|	type IDENT ';'
;

type:
		BIT
	|	type '[' NUM ']'
;


/*
stmt:
		%empty
	|	stmt line
;
line:
		'\n'
	|	expr '\n'	{ printf("   %g\n", $1); }
;
expr:
		NUM				{ $$ = $1; }
	|	expr expr '+'	{ $$ = $1 + $2; }
	|	expr expr '-'	{ $$ = $1 - $2; }
	|	expr expr '*'	{ $$ = $1 * $2; }
	|	expr expr '/'	{ $$ = $1 / $2; }
	|	expr expr '^'	{ $$ = pow($1, $2); }
	|	expr 'n'			{ $$ = -1 * $1; }
;
*/


plugtype_decl:
		"plugtype" IDENT '{' opt_plugtype_fields '}'
;

opt_plugtype_fields:
		/* empty */
	|	plugtype_fields
;

plugtype_fields:
		                plugtype_field
	|	plugtype_fields plugtype_field
;

plugtype_field:
		type IDENT opt_arrayDecls ';'
;


opt_arrayDecls:
		/* empty */
	|	arrayDecls
;

arrayDecls:
		           '[' expr ']'
	|	arrayDecls '[' expr ']'
;


%%


int main()
{
	return yyparse();
}

void yyerror(char const *s)
{
	fprintf(stderr, "%s\n", s);
}
