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
	#include "wiring/core.h"
}



/* these are the tokens which are not implicitly declared with "keyword"
 * down in the grammar below.
 */
%token<num> NUM
%token<str> STR

/* this generates the yytname[] table, used by tokenLookup() below */
%token-table

/* this generates the yyloc global variable (line and column information),
 * which lex fills because we have also set the %bison-locations option
 * inside our lexer.
 */
%locations



/* this declares the various types which can be stored in yylval. */
%union {
	int   num;
	char *str;

	HWC_Wiring *core;

	struct {
		int arrayLen;
		HWC_WiringMemory *array;
		int curCount;
	} mem;

	struct {
		int arrayLen;
		HWC_WiringLogic *array;
		int curCount;
	} logic;

	struct {
		int type;
		int binary;
	} logic_op;

	struct {
		int arrayLen;
		HWC_WiringConnection *array;
		int curCount;
	} connections;
}

%type<core>        file
%type<mem>         mem
%type<logic>       logic
%type<logic_op>    logic_op
%type<num>         logic_b_opt
%type<connections> connections
%type<num>         connection_opt_condition
%type<str>         opt_debug



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
	/* NOTE: one rule, several lines! */
	"version" ':' NUM '.' NUM
	"debug" '=' STR
	"bits" NUM
	mem
	logic
	connections
		{ assert($3 == 1 && $5 == 0);
		    // TODO: handle the debug string 

		  bisonParseRoot = $$ = malloc(sizeof(HWC_Wiring));
		  $$->numBits = $10;

		  assert($11.curCount == $11.arrayLen);
		  $$->numMemRanges = $11.arrayLen;
		  $$->mem          = $11.array;

		  assert($12.curCount == $12.arrayLen);
		  $$->numLogicalOperators = $12.arrayLen;
		  $$->logic               = $12.array;

		  assert($13.curCount == $13.arrayLen);
		  $$->numConnections = $13.arrayLen;
		  $$->conns          = $13.array;
		}
;


/* this is very strange!  We want to pre-allocate an array, and the file
 * tells us the proper length before we begin.  So we'll parse the first
 * line as the *DEEPEST* non-terminal, and then expand upon it with other
 * lines.
 *
 * Of course, this is left-associative parsing, which in other languages
 * could lead to ambigous parsing.  But in our simplified, keyword-heavy
 * language, that's never a problem.  The lookahead always tells us, with
 * complete unambiguity, what sort of element is coming next.
 */
mem:
		"memory" "count" NUM
			{ $$.arrayLen = $3;
			  $$.array = malloc($3 * sizeof(HWC_WiringMemory));
			  $$.curCount = 0; }

	|	mem "memory" "size" NUM "read" NUM "write" NUM opt_debug
			{ assert($1.curCount < $1.arrayLen);  // TODO: make this a syntax error

			  $$.arrayLen = $1.arrayLen;
			  $$.array    = $1.array;
			  $$.curCount = $1.curCount+1;
			  $$.array[$$.curCount-1].size  = $4;
			  $$.array[$$.curCount-1].read  = $6;
			  $$.array[$$.curCount-1].write = $8;
			  $$.array[$$.curCount-1].debug = $9; }
;

logic:
		"logic" "count" NUM
			{ $$.arrayLen = $3;
			  $$.array = malloc($3 * sizeof(HWC_WiringLogic));
			  $$.curCount = 0; }

	|	logic "logic" logic_op "size" NUM "a" NUM logic_b_opt "out" NUM opt_debug
			{ assert(($3.binary == 1) == ($8 != WIRING_BIT_INVALID));  // TODO: make this a syntax error

			  assert($1.curCount < $1.arrayLen);  // TODO: make this a syntax error

			  $$.arrayLen = $1.arrayLen;
			  $$.array    = $1.array;
			  $$.curCount = $1.curCount+1;
			  $$.array[$$.curCount-1].type  = $3.type;
			  $$.array[$$.curCount-1].size  = $5;
			  $$.array[$$.curCount-1].a     = $7;
			  $$.array[$$.curCount-1].b     = $8;
			  $$.array[$$.curCount-1].out   = $10;
			  $$.array[$$.curCount-1].debug = $11; }
;

logic_op:
		"AND"     { $$.type = WIRING_AND; $$.binary = 1; }
	|	"OR"      { $$.type = WIRING_OR;  $$.binary = 1; }
	|	"XOR"     { $$.type = WIRING_XOR; $$.binary = 1; }
	|	"NOT"     { $$.type = WIRING_NOT; $$.binary = 0; }
	|	"EQ"      { $$.type = WIRING_EQ;  $$.binary = 1; }
	|	"NEQ"     { $$.type = WIRING_NEQ; $$.binary = 1; }
;

logic_b_opt:
		%empty    { $$ = WIRING_BIT_INVALID; }
	|	"b" NUM   { $$ = $2;                 }
;

connections:
		"connection" "count" NUM
			{ $$.arrayLen = $3;
			  $$.array = malloc($3 * sizeof(HWC_WiringConnection));
			  $$.curCount = 0; }

	|	connections "connection" connection_opt_condition "size" NUM "to" NUM "from" NUM opt_debug
			{ assert($1.curCount < $1.arrayLen);  // TODO: make this a syntax error

			  $$.arrayLen = $1.arrayLen;
			  $$.array    = $1.array;
			  $$.curCount = $1.curCount+1;
			  $$.array[$$.curCount-1].size = $5;
			  $$.array[$$.curCount-1].to   = $7;
			  $$.array[$$.curCount-1].from = $9;
			  $$.array[$$.curCount-1].condition = $3;
			  $$.array[$$.curCount-1].isUndir   =  0;
			  $$.array[$$.curCount-1].debug     = $10; }
;

connection_opt_condition:
		%empty                    { $$ = WIRING_BIT_INVALID; }
	|	'(' "condition" NUM ')'   { $$ = $3;                 }
;

opt_debug:
		%empty            { $$ = NULL; }
	|	"debug" '=' STR   { $$ = $3;   }
;



%%

void yyerror(char const *s)
{
	printf("%s at line %d col %d\n", s, yylloc.first_line, yylloc.first_column);
}



/* NOTE: This is the same as the matching function in hwcCompile, except that
 *       IDENT tokens are not supported in this parser.  So we *always* assert
 *       that the token was found.
 */
int tokenLookup(char *str)
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
			return yytoknum[i];
		}
	}


	/* invalid keyword! */
	fprintf(stderr, "WIRING DIAGRAM PARSE ERROR: Invalid keyword '%s'\n", str);
	return 256;   // ERROR token
}

