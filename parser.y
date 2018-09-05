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
%token NUM
%token IDENT

/* Grammar Rules */
%%


/* Parses  */

/* Add a line type instead */


stmt:
		%empty
	|	'\n'
	|	'//' comment '\n'
	|	part
;

/* Just leave blank so it parses anything? */
comment:
;

/* Plan for empty parts */
part:
		"part" IDENT '{' part_stmts '}'
;

part_stmts:
		part_stmt part_stmts
	|	part_stmt
;

part_stmt:
		type IDENT ';'
;

type:
		"bit"
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
%%


int main()
{
	return yyparse();
}

void yyerror(char const *s)
{
	fprintf(stderr, "%s\n", s);
}



// This lexer is copied nearly verbatim from the sources listed in the header,
// except with minor modifications for my style of coding.
// Can only process integers.
/*
int yylex()
{
	int c;

	do
	{
		// Read any input in stdin, or wait for stdin input
		c = getchar();
		continue;
	} while(c == ' ' || c == '\t');

	// If a number is encountered
	if(isdigit(c))
	{
		ungetc(c, stdin);
		// This scans the whole number into one element on the stack
		scanf("%lf", &yylval);
		return NUM;
	}

	// If EOF or any non-number/non-whitespace is encountered
	if(c == EOF)
		return 0;
	else
		return c;
}
*/
