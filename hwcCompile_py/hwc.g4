grammar hwc;



file:
     decls+=typeDecl* EOF
;

typeDecl:
      'part' name=IDENT '{' stmts+=    stmt* '}'
    | 'plug' name=IDENT '{' decls+=declStmt* '}'
;



declStmt:
      ( mem='memory' '(' t=type ')' |
                         t=type     ) decls+=declNameInit (',' decls+=declNameInit)* ';'
;
declNameInit:
      name=IDENT ('=' val=expr)?
;



stmt:
      '{' stmts+=stmt* '}'                                      # stmt_Block

    | ('subpart'|'public'|'private'|'static') d=declStmt    # stmt_Decl

    | (lhs+=expr '=')+ rhs=expr ';'    # stmt_Connection

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
      /* NOTE: comparison operators are all lowest precedence, and non-associative */
      left=expr2 (('==' |
                   '!=' |

                   /* TODO: the lt/gt operators are only valid on int, not bit[] */
                   '<'  |
                   '>'  |
                   '<=' |
                   '>=')   right+=expr2)?   // right is not actually an array here, but I use that type of variable so that there's direct parallelism to expr[1-6].  Same code works in both places.
;

expr2:
      left=expr3 (('|'  |
                   '||' |
                   '^')   right+=expr3)*
;

expr3:
      left=expr4 (('&'  |
                   '&&')  right+=expr4)*
;

expr4:
      left=expr5 (('+' |
                   '-' |
                   ':')   right+=expr5)*
;

expr5:
      left=expr6 (('*' |
                   '/' |
                   '%')   right+=expr6)*
;

expr6:
      left=expr7 (('*' |
                   '/' |
                   '%')   right+=expr7)*
;

expr7:
      base=expr8

    | ('!' |
       '~' |
       '-')  right=expr7
;

expr8:
      base=expr9

    | left=expr8 '.' field=IDENT
    | left=expr8 '[' a=expr? (':' b=expr) ']'    /* TODO: [a:] is legal, [:b] is legal, [:] is not */
;

expr9:
      '(' subexpr=expr ')'
    | name =IDENT
    | num  =NUM
    | true ='true'
    | false='false'

      /* TODO: converts an integer to its bit-expression.  Only valid for non-negative.  Size
       *       is auto-detected; most users may prefer *assigning* an int to a well-known field.
       */
    | 'bits' '(' bitSize=expr ')'
;



IDENT: [a-zA-Z_][a-zA-Z_0-9]* ;
NUM  : ('0' | '-'? [1-9][0-9_]* | '0x'[0-9a-fA-F_]+ | '0b'[01_]+) ;

WS: [ \t\n]+ -> skip ;

