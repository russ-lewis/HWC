
/*
	A very rough parser for Hardware C
*/


/* Prologue C-statements */
%{
	#include <math.h>
	#include <stdio.h>
	#include <ctype.h>
	#include <string.h>
	int yylex(void);
	void yyerror(char const *);

	#define YYSTYPE char *

	/* https://stackoverflow.com/questions/6588624/yacc-bison-the-pseudo-variables-1-2-and-how-to-print-them-using-pri?rq=1 */
	extern char *yytext;
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
		Part Ident '{' part_stmts '}'		{ printf("User added a [%s] with name [%s]\n", $1, $2); }
;

part_stmts:
		part_stmts part_stmt
	|	part_stmt
;

part_stmt:
		%empty									/* ie, there can be an empty lines within parts */
	|	type Ident ';'							{ printf("-Statement of type [%s] with name [%s]\n", $1, $2); }
;

type:
		Bit
	|	type '[' Num ']'						{ printf("--Array of size [%s] declared\n", $3); }
;



/* Conversion to string for all tokens. See the link above "extern char" in the first section for more info. */
Part:
		PART		{ $$ = strdup(yytext); }
;
Bit:
		BIT		{ $$ = strdup(yytext); }
;
Num:
		NUM		{ $$ = strdup(yytext); }
;
Ident:
		IDENT		{ $$ = strdup(yytext); }
;



plugtype_decl:
		"plugtype" IDENT '{' opt_plugtype_fields '}'
;

opt_plugtype_fields:
		%empty
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
		%empty
	|	arrayDecls
;

arrayDecls:
		           '[' expr ']'
	|	arrayDecls '[' expr ']'
;



expr:
	    /* TODO: add lots more! */
	  Ident
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
