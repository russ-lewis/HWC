grammar hwc;



file:
     decls+=decl* EOF
;

decl:
      'part' IDENT '{'     stmt* '}'
    | 'plug' IDENT '{' declStmt* '}'
;



declStmt:
                   type     declList ';'    # declStmt_SimpleDecl

      /* TODO: forbid this in plugs */
    | 'memory' '(' type ')' declList ';'    # declStmt_MemoryDecl
;
declList:
      decls+=declInit (',' decls+=declInit)*
;
declInit:
      IDENT ('=' expr)?
;



stmt:
      '{' stmt* '}'                                           # stmt_Block

    | ( /*empty*/ | 'subpart'|'public'|'private') declStmt    # stmt_Decl

    | (expr '=')+ expr ';'    # stmt_Connection

/* TODO: add nested part and plugdecls
    | {variant in [0,1]}? 'part' '{' stmt* '}'    # stmt_Part
    |                     'plug' '{' stmt* '}'    # stmt_Plug
 */

/* TODO: add functions
    | 'function' IDENT '(' TODO ')' '{' TODO '}'    # stmt_Function
 */

    | 'static'? 'if' '(' expr ')' stmt ('else' stmt)    # stmt_If
    | 'for' '(' IDENT ';' expr '..' expr ')' stmt       # stmt_For

    | 'assert' '(' expr ')' ';'    # stmt_Assert

      /* TODO: add 'unittest' statements */
;



nameList:
      name+=IDENT (',' name+=IDENT)*     /* ANTLR generates a single array name[] because += */
;



type:
      IDENT                    # type_Named
    | type     '[' expr ']'    # type_Array
    | 'typeof' '(' expr ')'    # type_Typeof
    | 'bit'                    # type_Bit

    | 'int'                    # type_Int
    | 'bool'                   # type_Bool

      /* TODO: add support for this */
    | 'flag'                   # type_Flag
;



/* TODO: use antlr's precedence mechanisms to make this more elegant. */

expr:
      expr2

      /* NOTE: comparison operators are all lowest precedence, and non-associative */
    | expr2 ('==' |
             '!=' |

             /* TODO: the lt/gt operators are only valid on int, not bit[] */
             '<'  |
             '>'  |
             '<=' |
             '>=')  expr2
;

expr2:
      expr3

      /* left associative */
    | expr2 ('|'  |
             '||' |
             '^')   expr3
;

expr3:
      expr4

      /* left associative */
    | expr3 ('&'  |
             '&&')  expr4
;

expr4:
      expr5

      /* left associative */
    | expr4 ('+' |
             '-' |
             ':')  expr5
;

expr5:
      expr6

      /* left associative */
    | expr5 ('*' |
             '/' |
             '%')  expr6
;

expr6:
      expr7

      /* left associative */
    | expr6 ('*' |
             '/' |
             '%')  expr7
;

expr7:
      expr8
    | ('!' |
       '~' |
       '-')  expr7
;

expr8:
      expr9
    | expr8 '.' IDENT
    | expr8 '[' a=expr? (':' b=expr) ']'    /* TODO: [a:] is legal, [:b] is legal, [:] is not */
;

expr9:
      '(' expr ')'
    | IDENT
    | NUM
    | 'true'
    | 'false'

      /* TODO: converts an integer to its bit-expression.  Only valid for non-negative.  Size
       *       is auto-detected; most users may prefer *assigning* an int to a well-known field.
       */
    | 'bits' '(' expr ')'
;



IDENT: [a-zA-Z_][a-zA-Z_0-9]* ;
NUM  : ('-'? [1-9][0-9_]* | '0x'[0-9a-fA-F_]+ | '0b'[01_]+) ;

WS: [ \t\n]+ -> skip ;

