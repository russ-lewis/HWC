
/*
	A very rough parser for Hardware C
*/


/* Prologue C-statements */
%{
	#include <math.h>
	#include <stdio.h>
	#include <ctype.h>
	#include <string.h>
	#include <assert.h>

	#include "parsercommon.h"
	#include "pt/all.h"

	int yylex(void);
	void yyerror(char const *);


/* I don't have any need of this, but without it, Bison won't give me
 * access to yytoknum[].  (sigh).  -Russ
 * lol  -Jackson
 */
#define YYPRINT(fp, yychar, yylval)   do {} while(0)
%}



/* these are the tokens which are not implicitly declared with "keyword"
 * down in the grammar below.
 */
%token<str> NUM
%token<str> IDENT

/* this generates the yytname[] table, used by tokenLookup() below */
%token-table



/* this declares the various types which can be stored in yylval. */
%union {
	char *str;

	PT_file      *file;
	PT_file_decl *file_decl;

	PT_part_decl *part_decl;
	PT_part_stmt *part_stmt;

	PT_stmt *stmt;

	PT_plugtype_decl  *plugtype_decl;
	PT_plugtype_field *plugtype_field;

	PT_array_decl *array_decl;

	PT_type *type;

	PT_expr *expr;
}

%type<file>      file
%type<file_decl> file_decls
%type<file_decl> file_decl

%type<part_decl> part_decl
%type<part_stmt> opt_part_stmts
%type<part_stmt> part_stmts
%type<part_stmt> part_stmt

%type<stmt> opt_stmts
%type<stmt>	stmts
%type<stmt> stmt
%type<stmt> for_opts
%type<stmt> if_opts
%type<stmt> else_opts

%type<plugtype_decl>  plugtype_decl
%type<plugtype_field> opt_plugtype_fields
%type<plugtype_field> plugtype_fields
%type<plugtype_field> plugtype_field

%type<array_decl> opt_array_decls
%type<array_decl> array_decls

%type<type> type

%type<expr> expr
%type<expr> expr2
%type<expr> expr3
%type<expr> expr4


/* Grammar Rules */
%%



file:
		%empty             { $$ = malloc(sizeof(PT_file));
		                     $$->decls = NULL; }

	|	file_decls         { $$ = malloc(sizeof(PT_file));
		                     $$->decls = $1; 
									printf("---Debug output begins?---\n");
									dump_file($$, 0); }
;

file_decls:
		           file_decl   { $$ = $1; $$->prev = NULL; }
	|	file_decls file_decl   { $$ = $2; $$->prev = $1;   }
;

file_decl:
		part_decl        { $$ = malloc(sizeof(PT_file_decl));
		                   $$->partDecl = $1; }

	|	plugtype_decl    { $$ = malloc(sizeof(PT_file_decl));
		                   $$->plugtypeDecl = $1; }
;



part_decl:
		"part" IDENT '{' opt_part_stmts opt_stmts '}'
		                 { printf("User added a [part] with name [%s]\n", $2);
		                   $$ = malloc(sizeof(PT_part_decl));
		                   $$->name       = $2;
		                   $$->part_stmts = $4;
								 $$->stmts      = $5; }
;

opt_part_stmts:
		%empty       { $$ = NULL; }
	|	part_stmts   { $$ = $1; }
;

part_stmts:
		           part_stmt   { $$ = $1; $$->prev = NULL; }
	|	part_stmts part_stmt   { $$ = $2; $$->prev = $1;   }
;

part_stmt:
		"public" type IDENT ';'   { printf("-Public statement of type [-TODO-] with name [%s]\n", $3);
		                   $$ = malloc(sizeof(PT_part_stmt));
		                   $$->type = $2;
			                $$->name = $3;
								 $$->isPub = 1; }
	|	"private" type IDENT ';'   { printf("-Private statement of type [-TODO-] with name [%s]\n", $3);
		                   $$ = malloc(sizeof(PT_part_stmt));
		                   $$->type = $2;
			                $$->name = $3;
								 $$->isPub = 0; }
;

/* Code structure copied from opt_part_stmts */
opt_stmts:
		%empty	{ $$ = NULL; }
	|	stmts		{ $$ = $1;   }
;

/* Ask: How are stmts different from part_stmts? I presume the difference is that part_stmts cannot occur in plugtypes */
/* Code structure copied from part_stmts */
stmts:
				stmt		{ $$ = $1; $$->prev = NULL; }
	|	stmts stmt		{ $$ = $2; $$->prev = $1; }
;


stmt:
		expr '=' expr ';'											{  printf("-Statement of expr = expr\n");
									 										$$ = malloc(sizeof(PT_stmt));
																			$$->mode  = STMT_CONN;
																			$$->lHand = $1;
																			$$->rHand = $3; }
	|	"for" '(' expr ';' NUM ".." NUM ')' for_opts		{	printf("-Statement of for loop\n");
																			$$ = malloc(sizeof(PT_stmt));
																			$$->mode     = STMT_FOR;
																			$$->forVar   = $3;
																			$$->forBegin = $5;
																			$$->forEnd   = $7; 
																			$$->forStmts = $9; }
	| "if" '(' expr ')' if_opts								{	printf("-Statement of if stmt\n");
																			$$ = malloc(sizeof(PT_stmt));
																			$$->mode    = STMT_IF;
																			$$->ifExpr  = $3;
																			$$->ifStmts = $5;
																			$$->ifElse  = NULL; }
	| "else" else_opts											{	printf("-Statement of else stmt\n");
																			$$ = malloc(sizeof(PT_stmt));
																			$$->mode      = STMT_ELSE;
																			$$->elseStmts = $2; }
;

/* If there ARE NO curly braces, there must be some sort of stmt to iterate the for loop over. */
/* If there ARE    curly braces, there can be opt_stmts, meaning zero to a buncha stmts */
for_opts:
		stmt						{ $$ = $1; }
	|	'{' opt_stmts '}'		{ $$ = $2; }
;

/* Maybe combine this and for_opts in some way?
/*		The 'if' HAS NO 'else' and HAS NO curly braces */
/* 	The 'if' HAS NO 'else' and HAS    curly braces */
if_opts:
		stmt						{ $$ = $1; }
	|	'{' opt_stmts '}'		{ $$ = $2; }
;

/* Since else_opts checks for "else" and then a single stmt, it could potentially detect an [if...else if(expr)...else] chain */
else_opts:
		stmt						{ $$ = $1; }
	|	'{' opt_stmts '}'		{ $$ = $2; }
;

plugtype_decl:
		"plugtype" IDENT '{' opt_plugtype_fields '}'
		                 { $$ = malloc(sizeof(PT_plugtype_decl));
		                   $$->name   = $2;
		                   $$->fields = $4; }
;

opt_plugtype_fields:
		%empty           { $$ = NULL; }
	|	plugtype_fields  { $$ = $1;   }
;

plugtype_fields:
		                plugtype_field   { $$ = $1; $$->prev = NULL; }
	|	plugtype_fields plugtype_field   { $$ = $2; $$->prev = $1;   }
;

plugtype_field:
		type IDENT opt_array_decls ';'
		                 { $$ = malloc(sizeof(PT_plugtype_field));
		                   $$->type = $1;
		                   $$->name = $2;
		                   $$->arraySuffix = $3; }
;


opt_array_decls:
		%empty            { $$ = NULL; }
	|	array_decls       { $$ = $1;   }
;

array_decls:
		            '[' expr ']'
		                  { $$ = malloc(sizeof(PT_array_decl));
		                    $$->size = $2;
		                    $$->prev = NULL; }

	|	array_decls '[' expr ']'
		                  { $$ = malloc(sizeof(PT_array_decl));
		                    $$->size = $3;
		                    $$->prev = $1; }

;



type:
		"bit"              { $$ = malloc(sizeof(PT_type));
		                     $$->mode = TYPE_BIT; }
	|	IDENT					 { $$ = malloc(sizeof(PT_type));
									$$->mode  = TYPE_IDENT;
									$$->ident = $1; }
		// TODO: replace NUM with expr!
		// Is the right way to do this?
	|	type '[' expr2 ']'   { printf("--Array of size [EXPR] declared\n");
		                     $$ = malloc(sizeof(PT_type));
		                     $$->mode = TYPE_ARRAY;
		                     $$->base = $1;
		                     $$->len  = $3; }
;



expr:
		expr2
	|	expr2 "==" expr2			{	$$ = malloc(sizeof(PT_expr));
											$$->mode  = EXPR_EQUAL;
											$$->lHand = $1;
											$$->rHand = $3; }
;

expr2:
		expr3
	|	'!' expr2				{ /* TODO */ }
;

expr3:
		expr4
	|	expr3 '[' expr2 ']'   { /* TODO */ }
;

expr4:
		IDENT						{	$$ = malloc(sizeof(PT_expr));
										$$->mode = EXPR_IDENT;
										$$->name = $1; }
	|	NUM						{	$$ = malloc(sizeof(PT_expr));
										$$->mode = EXPR_NUM;
										$$->num  = $1; }
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



/* this looks up a possible-IDENT in a table of strings generated by Bison; if
 * we find it, then we return the correct ID for that keyword.  But if we don't
 * find it, then strdup() the string to a new string, save it into yylval, and
 * then report an IDENT.
 *
 * Note that if assertFound==1, then we won't support the IDENT case at the
 * end.
 */
int tokenLookup(char *str, int assertFound)
{
	int i;
	int len = strlen(str);

	/* YYNTOKENS is the number of defined tokens in the table.  The table
	 * of strings is the array yytname[].
	 *
	 * Since we're always looking for double-quoted strings, the string
	 * at each entry that we care about will be
	 *       "keyword"
	 * or
	 *       "<="
	 *
	 * So, we'll perform several checks in a row:
	 *    - Is the first character of the string a double-quote?
	 *    - Is the string immediately after that, continuing for the
	 *      length of our target string, an exact match?
	 *    - After that, do we have another double-quote?
	 *    - After that, do we have a null terminator?
	 *
	 * If all of these checks pass, then the string in yytname[i] matches
	 * what we're lexing, so we look up the token ID in yytoknum[i] and
	 * return that.
	 *
	 * If we fail these checks for *ALL* of the tokens in the table, then
	 * this is an actual identifier (if allowed).
	 */
	for(i=0; i<YYNTOKENS; i++)
	{
		if(yytname[i] != NULL                   &&
		   yytname[i][0] == '"'                 &&
		   strncmp(yytname[i]+1, str, len) == 0 &&
		   yytname[i][len+1] == '"'             &&
		   yytname[i][len+2] == '\0')
		{
	printf("tokenLookup(): str=\"%s\" returning %d\n", str, yytoknum[i]);

			return yytoknum[i];
		}
	}


	/* if we get here, then we failed the search.  Was that expected to
	 * be possible?
	 */
	if (assertFound)
	{
		assert(0);   // TODO
	}

printf("tokenLookup(): str=\"%s\" returning IDENT\n", str);
	/* otherwise, save the string in the yylval, and we can return */
	yylval.str = strdup(str);
	return IDENT;
}

