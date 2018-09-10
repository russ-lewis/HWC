/* RUSS WAS HERE TOO */

%{
#include <stdlib.h>
#include <string.h>

#include "ctod_intf.h"
#include "parsercommon.h"

#define YYDEBUG 1

int   lineNum = 1;

#define SyntaxCheck(expr)                           \
if(!(expr))                                         \
{                                                   \
  fflush(NULL);                                     \
  yyerror("Grammar assertion failed: '" #expr "'"); \
  exit(1);                                          \
}

%}


%token IDENTIFIER
%token TOKEN
%token NUM
%token D_BLOCK


%{
#define YYPRINT(fp, yychar, yylval) \
  if(yychar == IDENTIFIER || yychar == TOKEN) \
    fprintf(fp, "=%s", yylval)


%}

%token_table

%union {
  void                *ptr;
/*
  _auto_0             *auto_0;
  _auto_1             *auto_1;
  _nt_rules           *rules;
  _nt_rule_qualifiers *rule_qualifiers;
  _nt_rule_pattern    *rule_pattern;
  _nt_rule_element    *rule_element;
    _nt_rule_element__base   *rule_element__base;
    _nt_rule_element__limits *rule_element__limits;
  _nt_elem_name       *elem_name;
*/
  char                *string;
  unsigned long        num;
}

/*
%type <auto_0>          _auto_0
%type <auto_1>          _auto_1
%type <rules>           rules
%type <rule_qualifiers> rule_qualifiers
%type <rule_pattern>    rule_pattern
%type <rule_element>    rule_element
  %type <rule_element__base>   rule_element__base
  %type <rule_element__limits> rule_element__limits
%type <elem_name>       elem_name
*/

%type <ptr>    rules__rule
%type <ptr>    rules
%type <ptr>    rule_qualifiers
%type <ptr>    rule_qualifiers__rule_qualifier
%type <ptr>    elements
%type <ptr>    rule_pattern__opt
%type <ptr>    rule_pattern__prec
%type <ptr>    rule_pattern
%type <ptr>    rule_element__base
%type <ptr>    rule_element__limits
%type <ptr>    rule_element
%type <ptr>    elem_name
%type <string> IDENTIFIER
%type <string> TOKEN
%type <string> D_BLOCK
%type <num>    NUM



%%



START:
	  /* empty */
	    { return Cebu_Callback(Do_parse0("rules:")); }
	| rules
	    { return Cebu_Callback($1); }
;

rules__rule:
/* models: IDENTIFIER rule_qualifiers? ':' rule_pattern ';'
 *       | D_BLOCK
 *       | "%token" IDENTIFIER CBLOCK
 */
	  IDENTIFIER rule_qualifiers ':' rule_pattern ';'
	    { $$ = Do_parse3("rules__rule: IDENTIFIER rule_qualifiers ':' rule_pattern ';'", $1,$2,$4); }
	| IDENTIFIER                 ':' rule_pattern ';'
	    { $$ = Do_parse2("rules__rule: IDENTIFIER ':' rule_pattern ';'", $1,$3); }
	| D_BLOCK
	    { $$ = Do_parse1("rules__rule: D_BLOCK", $1); }
	| "%token" IDENTIFIER D_BLOCK
	    { $$ = Do_parse2("rules__rule: \"%token\" IDENTIFIER D_BLOCK", $2,$3); }
	| "%opt" IDENTIFIER D_BLOCK
	    { $$ = Do_parse2("rules__rule: \"%opt\" IDENTIFIER D_BLOCK", $2,$3); }
;

rules:
	  rules__rule
	    { $$ = Do_parse1("rules: rules__rule", $1); }
	| rules rules__rule
	    { $$ = Do_parse2("rules: rules rules__rule", $1,$2); }
;

rule_qualifiers:
	  rule_qualifiers__rule_qualifier
	    { $$ = Do_parse1("rule_qualifiers: rule_qualifier__rule_qualifier", $1); }
	| rule_qualifiers rule_qualifiers__rule_qualifier
	    { $$ = Do_parse2("rule_qualifiers: rule_qualifiers rule_qualifier__rule_qualifier", $1,$2); }
;

rule_qualifiers__rule_qualifier:
	  "%opt" IDENTIFIER D_BLOCK
	    { $$ = Do_parse2("rule_qualifiers__rule_qualifier: \"%opt\" IDENTIFIER D_BLOCK", $2,$3); }
;

elements:
/* models: rule_element+
 */
	  rule_element
	    { $$ = Do_parse1("elements: rule_element", $1); }
	| elements rule_element
	    { $$ = Do_parse2("elements: elements rule_element", $1,$2); }
;

rule_pattern__opt:
	  /* empty */
	    { $$ = Do_parse0("rule_pattern__opt: /* empty */"); }
	| elements
	    { $$ = Do_parse1("rule_pattern__opt: elements", $1); }
	|          "opt" IDENTIFIER
	    { $$ = Do_parse1("rule_pattern__opt: \"opt\" IDENTIFIER", $2); }
	| elements "opt" IDENTIFIER
	    { $$ = Do_parse2("rule_pattern__opt: elements \"opt\" IDENTIFIER", $1,$3); }
//	| "prec_left" ':' rule_pattern__opt
//	    { $$ = Do_parse1("rule_pattern__opt: \"prec_left\" ':' rule_pattern__opt", $3); }
//	| "prec_right" ':' rule_pattern__opt
//	    { $$ = Do_parse1("rule_pattern__opt: \"prec_right\" ':' rule_pattern__opt", $3); }
//	| "prec" ':' rule_pattern__opt
//	    { $$ = Do_parse1("rule_pattern__opt: \"prec\" ':' rule_pattern__opt", $3); }
;

rule_pattern:
	  rule_pattern__prec
	    { $$ = Do_parse1("rule_pattern: rule_pattern__prec", $1); }
	| rule_pattern "%none"  rule_pattern__prec
	    { $$ = Do_parse2("rule_pattern: rule_pattern \"%none\" rule_pattern__prec", $1,$3); }
	| rule_pattern "%left"  rule_pattern__prec
	    { $$ = Do_parse2("rule_pattern: rule_pattern \"%left\" rule_pattern__prec", $1,$3); }
	| rule_pattern "%right" rule_pattern__prec
	    { $$ = Do_parse2("rule_pattern: rule_pattern \"%right\" rule_pattern__prec", $1,$3); }
;

rule_pattern__prec:
	  rule_pattern__opt
	    { $$ = Do_parse1("rule_pattern__prec: rule_pattern__opt", $1); }
	| rule_pattern__prec '|' rule_pattern__opt
	    { $$ = Do_parse2("rule_pattern__prec: rule_pattern__prec '|' rule_pattern__opt", $1,$3); }
;

rule_element__base:
/* models: rule_element
 *       | '[' elements ',' elements? ']'
 */
	  rule_element
	    { $$ = Do_parse1("rule_element__base: rule_element", $1); }
	| '[' elements ','         ']'
	    { $$ = Do_parse1("rule_element__base: '[' elements ',' ']'", $2); }
	| '[' elements ',' elements ']'
	    { $$ = Do_parse2("rule_element__base: '[' elements ',' elements ']'", $2,$4); }
;

rule_element__limits:
/* models: '+' | '*'
 *       | '{' NUM ( ',' NUM? )? '}'
 */
	  '+'
	    { $$ = Do_parse0("rule_element__limits: '+'"); }
	| '*'
	    { $$ = Do_parse0("rule_element__limits: '*'"); }
	| '{' NUM         '}'
	    { $$ = Do_parse1("rule_element__limits: '{' NUM '}'", (void*)$2); }
	| '{' NUM ','     '}'
	    { $$ = Do_parse1("rule_element__limits: '{' NUM ',' '}'", (void*)$2); }
	| '{' NUM ',' NUM '}'
	    { $$ = Do_parse2("rule_element__limits: '{' NUM ',' NUM '}'", (void*)$2,(void*)$4); }
;

rule_element:
	  '(' rule_pattern ')' elem_name
	    { $$ = Do_parse2("rule_element: '(' rule_pattern ')' elem_name", $2,$4); }
	| '(' rule_pattern ')'
	    { $$ = Do_parse1("rule_element: '(' rule_pattern ')'", $2); }
	| rule_element__base rule_element__limits elem_name
	    { $$ = Do_parse3("rule_element: rule_element__base rule_element__limits elem_name", $1,$2,$3); }
	| rule_element__base rule_element__limits
	    { $$ = Do_parse2("rule_element: rule_element__base rule_element__limits", $1,$2); }
	| rule_element '?'
	    { $$ = Do_parse1("rule_element: rule_element '?'", $1); }
	| IDENTIFIER elem_name
	    { $$ = Do_parse2("rule_element: IDENTIFIER elem_name", $1,$2); }
	| IDENTIFIER
	    { $$ = Do_parse1("rule_element: IDENTIFIER", $1); }
        | TOKEN elem_name
	    { $$ = Do_parse2("rule_element: TOKEN elem_name", $1,$2); }
	| TOKEN
	    { $$ = Do_parse1("rule_element: TOKEN", $1); }
	| "assert" D_BLOCK
	    { $$ = Do_parse1("rule_element: \"assert\" D_BLOCK", $2); }
	| D_BLOCK
	    { $$ = Do_parse1("rule_element: D_BLOCK", $1); }
;

elem_name:
	  '=' IDENTIFIER
	    { $$ = Do_parse1("elem_name: '=' IDENTIFIER", $2); }
;



%%

char *AddToTokenTable(char*);
int FindInTokenTable(char *str)
{
  int i;
  int len = strlen(str);

  for(i=0; i<YYNTOKENS; i++)
    if(yytname[i] != NULL                   &&
       yytname[i][0] == '"'                 &&
       strncmp(yytname[i]+1, str, len) == 0 &&
       yytname[i][len+1] == '"'             &&
       yytname[i][len+2] == '\0')
      return yytoknum[i];

  yylval.string = AddToTokenTable(str);

  return IDENTIFIER;
}

FILE *input_save;

yyerror(char *s)
{
  if(yydebug == 0)
  {
    printf("\n\n%s at line %d; rerunning with debug=1\n",s,lineNum);
    yydebug = 1;
    lineNum = 1;
    rewind(input_save);
    init_lex(input_save);
    fflush(NULL);
    exit(yyparse());
  }
  else
  {
    printf("%s at line %d\n", s,lineNum);
  }
}

int Cebu_Parse(FILE *input)
{
  yydebug = 0;

  input_save = input;
  init_lex(input);

  return yyparse();
}

