/*
 *  The parser for Hardware C source code
 */


/* Prologue C-statements */
%{
	#include <math.h>
	#include <stdio.h>
	#include <ctype.h>
	#include <string.h>
	#include <assert.h>

	int yylex(void);
	void yyerror(char const *);


/* I don't have any need of this, but without it, Bison won't give me
 * access to yytoknum[].  (sigh).  -Russ
 * lol  -Jackson
 */
#define YYPRINT(fp, yychar, yylval)   do {} while(0)
%}

/* the block above is code which is *ONLY* dropped into the parser's .c
 * file.  This block is code that needs to be in *BOTH* the .c and .h
 * files.
 *
 * https://www.gnu.org/software/bison/manual/html_node/_0025code-Summary.html#g_t_0025code-Summary
 *
 * (Thanks to Stack Overflow for helping me find this page.)
 */
%code requires {
	#include "parsercommon.h"
	#include "pt/all.h"
}



/* these are the tokens which are not implicitly declared with "keyword"
 * down in the grammar below.
 */
%token<str> NUM
%token<str> IDENT

/* this generates the yytname[] table, used by tokenLookup() below */
%token-table

/* this generates the yyloc global variable (line and column information),
 * which lex fills because we have also set the %bison-locations option
 * inside our lexer.
 */
%locations



/* this declares the various types which can be stored in yylval. */
%union {
	char *str;

	PT_file      *file;
	PT_file_decl *file_decl;

	PT_part_decl *part_decl;
	PT_plugtype_decl  *plugtype_decl;

	PT_stmt *stmt;
	PT_decl *decl;

	PT_array_decl *array_decl;

	PT_type *type;

	PT_expr *expr;
}

%type<file>      file
%type<file_decl> file_decls
%type<file_decl> file_decl

%type<part_decl> part_decl
%type<stmt> opt_stmts
%type<stmt> stmts
%type<stmt> stmt

%type<plugtype_decl>  plugtype_decl
%type<decl> opt_fields
%type<decl> fields
%type<decl> field

%type<array_decl> opt_array_decls
%type<array_decl> array_decls

%type<type> type

%type<expr> expr
%type<expr> expr2
%type<expr> expr3
%type<expr> expr4
%type<expr> expr5


/* this solves the if-else chaining problem.  Canonical example is the
 * shift-reduce conflict that happens in this example code:
 *      if (a)
 *        if (a)
 *          stmt
 *        else
 *          stmt
 */
%right "if" "else"


/* Grammar Rules */
%%



/* it feels terribly wrong to me to modify a global variable inside the
 * reduction code.  However, I can't find any way to access the 'file'
 * that we've created here, except in this way.  If bison provides a
 * "correct" global variable, which represents the root of the parse
 * tree, I haven't found it.
 *
 * I believe that I could fix this, more "correctly," by changing the
 * options to tell Bison to generate a reentrant parser (because then
 * yylval would be a pointer, not a global).  Maybe I'll make that
 * change later.
 *
 * UPDATE: It appears that the 'reentrant' parser only affects the
 *         parser/lexer calling convention; it doesn't affect yyparse().
 *         However, there are options which allow you to add your own,
 *         custom parameters to yyparse():
 *
 *         https://www.gnu.org/software/bison/manual/html_node/Pure-Calling.html#Pure-Calling
 *
 *       - Russ 3 Oct 2018
 */

file:
		%empty           { $$ = malloc(sizeof(PT_file));
		                   $$->decls = NULL;
		                   bisonParseRoot = $$; }

	|	file_decls       { $$ = malloc(sizeof(PT_file));
		                   $$->decls = $1;
		                   bisonParseRoot = $$; }
;

file_decls:
		           file_decl   { $$ = $1; $$->prev = NULL; }
	|	file_decls file_decl   { $$ = $2; $$->prev = $1;   }
;

file_decl:
		part_decl        { $$ = malloc(sizeof(PT_file_decl));
		                   $$->partDecl     = $1;
		                   $$->plugtypeDecl = NULL; }

	|	plugtype_decl    { $$ = malloc(sizeof(PT_file_decl));
		                   $$->partDecl     = NULL;
		                   $$->plugtypeDecl = $1; }
;



part_decl:
		"part" IDENT '{' opt_stmts '}'
		                 { // printf("User added a [part] with name [%s]\n", $2);
		                   $$ = malloc(sizeof(PT_part_decl));
		                   $$->name  = $2;
		                   $$->stmts = $4; }
;

opt_stmts:
		%empty  { $$ = NULL; }
	|	stmts   { $$ = $1; }
;

stmts:
		      stmt   { $$ = $1; $$->prev = NULL; }
	|	stmts stmt   { $$ = $2; $$->prev = $1;   }
;

stmt:
		'{'       '}'              { $$ = NULL; } /* NOP STATEMENT */

	|	'{' stmts '}'              { $$ = $2; }   /* TODO: make this an actual
		                                           * nested type, since it's a
		                                           * name scope.
		                                           *
		                                           * BUG BUG BUG - we'll lose all
		                                           * but the last stmt when this
		                                           * is linked to another!
		                                           */

	|	"public"  field
		                           { $$ = malloc(sizeof(PT_stmt));
		                             $$->mode     = STMT_DECL;
		                             $$->isPublic = 1;
		                             $$->stmtDecl = $2; }
	|	"private" field
		                           { $$ = malloc(sizeof(PT_stmt));
		                             $$->mode     = STMT_DECL;
		                             $$->isPublic = 0;
		                             $$->stmtDecl = $2; }
	|	expr '=' expr ';'
		                           { printf("-Statement of expr = expr\n");
		                             $$ = malloc(sizeof(PT_stmt));
		                             $$->mode  = STMT_CONN;
		                             $$->lHand = $1;
		                             $$->rHand = $3; }
	|	"for" '(' IDENT ';' expr ".." expr ')' stmt
		                           { printf("-Statement of for loop\n");
		                             $$ = malloc(sizeof(PT_stmt));
		                             $$->mode     = STMT_FOR;
		                             $$->forVar   = $3;
		                             $$->forBegin = $5;
		                             $$->forEnd   = $7; 
		                             $$->forStmts = $9; }

		/* THIS IS A WEIRD HACK TO MAKE BISON WORK.
		 *
		 * Bison says that "the rule gets its precedence from the last
		 * terminal symbol" - so, by default, this has the precedence
		 * of the ')' token.  We explicitly must set the precedence
		 * here.
		 *
		 * However, that is not required in the "else" case, since it
		 * gets its precedence from "else".
		 */
	|	%prec "if"
		"if" '(' expr ')' stmt
		                       { printf("-Statement of if stmt\n");
		                         $$ = malloc(sizeof(PT_stmt));
		                         $$->mode    = STMT_IF;
		                         $$->ifExpr  = $3;
		                         $$->ifStmts = $5;
		                         $$->ifElse  = NULL; }
	|	"if" '(' expr ')' stmt "else" stmt
		                                   { printf("-Statement of if stmt\n");
		                                     $$ = malloc(sizeof(PT_stmt));
		                                     $$->mode    = STMT_IF;
		                                     $$->ifExpr  = $3;
		                                     $$->ifStmts = $5;
		                                     $$->ifElse  = $7; }

	|	"assert" '(' expr ')' ';'
		                          { printf("-Statement of assertion\n");
		                            $$ = malloc(sizeof(PT_stmt));
		                            $$->mode      = STMT_ASRT;
		                            $$->assertion = $3; }
;


plugtype_decl:
		"plugtype" IDENT '{' opt_fields '}'
		                  { $$ = malloc(sizeof(PT_plugtype_decl));
		                    $$->name   = $2;
		                    $$->fields = $4; }
;

opt_fields:
		%empty  { $$ = NULL; }
	|	fields  { $$ = $1;   }
;

fields:
		       field   { $$ = $1; $$->prev = NULL; }
	|	fields field   { $$ = $2; $$->prev = $1;   }
;

field:
		type IDENT opt_array_decls ';'
		                 { $$ = malloc(sizeof(PT_decl));
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
	|	IDENT              { $$ = malloc(sizeof(PT_type));
		                     $$->mode  = TYPE_IDENT;
		                     $$->ident = $1; }
	/* I've tried to be clever here and use 'expr2' to exclude 'expr == expr' within brackets. This may have to change eventually. */
	|	type '[' expr2 ']'   { printf("--Array of size [EXPR] declared\n");
		                       $$ = malloc(sizeof(PT_type));
		                       $$->mode = TYPE_ARRAY;
		                       $$->base = $1;
		                       $$->len  = $3; }
;



expr:
		expr2
	|	expr2 "==" expr2   { $$ = malloc(sizeof(PT_expr));
		                     $$->mode  = EXPR_EQUAL;
		                     $$->lHand = $1;
		                     $$->rHand = $3; }
;

expr2:
		expr3
	|	'!' expr2          { $$ = malloc(sizeof(PT_expr));
		                     $$->mode    = EXPR_NOT;
		                     $$->notExpr = $2; }
;

expr3:
		expr4
	/* I've tried to be clever here and use 'expr2' to exclude 'expr == expr' within brackets. This may have to change eventually. */
	|	expr3 '[' expr2 ']'   { $$ = malloc(sizeof(PT_expr));
		                        $$->mode      = EXPR_ARR;
		                        $$->arrayExpr = $1;
		                        $$->indexExpr = $3; }
;

expr4:
		expr5
	|	expr4 '.' expr5       /* Do we allow expr.expr.expr.expr endlessly, or only expr.expr? I think it's the later, but I made it the former just in case */
		                      /* Do we allow expr4.expr3[expr2]? This code doesn't allow for that, and shift/reduce conflicts are created when I try. */
		                      /*    Fixing the above shift/reduce conflict idea: Swap expr3 and expr4's components. */
                            { $$ = malloc(sizeof(PT_expr));
		                        $$->mode    = EXPR_DOT;
		                        $$->dotExpr = $1;
		                        $$->field   = $3; }
;

expr5:
		IDENT                 { $$ = malloc(sizeof(PT_expr));
		                        $$->mode = EXPR_IDENT;
		                        $$->name = $1; }
	|	NUM                   { $$ = malloc(sizeof(PT_expr));
		                        $$->mode = EXPR_NUM;
		                        $$->num  = $1; }
;



%%

void yyerror(char const *s)
{
	printf("%s at line %d col %d\n", s, yylloc.first_line, yylloc.first_column);
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
// printf("tokenLookup(): str=\"%s\" returning %d\n", str, yytoknum[i]);

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

// printf("tokenLookup(): str=\"%s\" returning IDENT\n", str);
	/* otherwise, save the string in the yylval, and we can return */
	yylval.str = strdup(str);
	return IDENT;
}

