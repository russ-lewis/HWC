grammar hwc;



file:
     decls+=partOrPlugDecl* EOF
;

partOrPlugDecl:
      (isPart='part' | isPart='plug') name=IDENT '{' stmts+=stmt* '}'
;



declNameInit:
      name=IDENT ('=' val=expr)?
;



stmt:
      '{' stmts+=stmt* '}'                                      # stmt_Block

    | (prefix=('subpart'|'public'|'private'|'static'))?
      ( mem='memory' '(' t=expr ')' | t=expr )
      decls+=declNameInit (',' decls+=declNameInit)* ';'        # stmt_Decl

    | (lhs+=expr '=')+ rhs=expr ';'    # stmt_Connection

    | static='static'? 'if' '(' cond=expr ')' tru_=stmt (els_='else' fals_=stmt)?    # stmt_If

    | 'for' '(' var=IDENT ';' start=expr '..' end=expr ')' body=stmt ('as' tuple_name=IDENT)?       # stmt_For

    | 'assert' '(' exp_=expr ')' ';'    # stmt_Assert

      /* TODO: add 'unittest' statements */
;



expr:
      /* NOTE: comparison operators are all lowest precedence, and non-associative */
      left=expr2 (op=('==' |
                      '!=' |

                      /* TODO: the lt/gt operators are only valid on int, not bit[] */
                      '<'  |
                      '>'  |
                      '<=' |
                      '>=')   right+=expr2)?   // right is not actually an array here, but I use that type of variable so that there's direct parallelism to expr[1-6].  Same code works in both places.
;

expr2:
      left=expr3a (op=('|'  |
                       '||' |
                       '^')   right+=expr3a)*
;

expr3a:      // TODO: re-number the expressions to get rid of the [ab] suffix
      left=expr3b (op=('&'  |
                       '&&')  right+=expr3b)*
;

expr3b:
      left=expr4 (op=('<<' |
                      '>>')  right+=expr4)*
;

expr4:
      left=expr5 (op=('+' |
                      '-')   right+=expr5)*
;

expr5:
      left=expr6 (op=('*' |
                      '/' |
                      '%')   right+=expr6)*
;

expr6:
      left=expr7 (op=('*' |
                      '/' |
                      '%')   right+=expr7)*
;

expr7:
      base=expr8
    | op=('!' | '-' | '~')  right=expr7
;

expr8:
      base=expr9

    | left=expr8 '.' field=IDENT
    | left=expr8 '['                         ']'    // only valid for field declarations
    | left=expr8 '[' a=expr                  ']'
    | left=expr8 '[' a=expr colon=':'        ']'
    | left=expr8 '['        colon=':' b=expr ']'
    | left=expr8 '[' a=expr colon=':' b=expr ']'
;

// # TODO: should 'typeof', 'len', and 'cast' be removed from the grammar, and a
// #       general-purpose function-call expression be added?  We could say, at
// #       first, that these 3 are the only allowed functions; later, we could say
// #       that they are *special* functions, and that no top-level function can
// #       have a conflicting name.
expr9:
      '(' subexpr=expr ')'
    | name =IDENT
    | num  =NUM
    | 'true'
    | 'false'

    | 'bit'
    | 'flag'

    | 'auto'

      /* TODO: converts an integer to its bit-expression.  Only valid for non-negative.  Size
       *       is auto-detected; most users may prefer *assigning* an int to a well-known field.
       * 
       * REMVOED: 'bits'   '('   bits_expr=expr ')'
       *
       * NEWER FORM is auto-types initialization:
       #           bit[] the_bits = expr;
       */

    | funcName='concat' '(' concatLeft=expr ',' concatRight=expr ')'

    | funcName='typeof' '(' typeof_expr=expr ')'
    | funcName='len'    '('    len_expr=expr ')'

    | 'cast' '(' castType=expr ',' castVal=expr ')'

    | 'int'
    | 'bool'
;



IDENT: [a-zA-Z_][a-zA-Z_0-9]* ;
NUM  : ('0' | '-'? [1-9][0-9_]* | '0x'[0-9a-fA-F_]+ | '0b'[01_]+) ;

WS: [ \t\r\n]+ -> skip ;

LINE_COMMENT: '//' ~('\r' | '\n')* -> skip ;    /* https://stackoverflow.com/questions/7070763/parse-comment-line   and    https://tomassetti.me/antlr-mega-tutorial/#chapter58 */

BLOCK_COMMENT: '/*' .*? '*/' -> skip ;    /* https://stackoverflow.com/questions/12898052/antlr-how-to-skip-multiline-comments */

