#ifndef _PARSER_COMMON_H__INCLUDED_
#define _PARSER_COMMON_H__INCLUDED_



// declared and maintained by the lexer
extern int lineNum, colNum;



// implemented by the code in the parser, called by the lexer.
int tokenLookup(char *str, int assertFound);



#endif

