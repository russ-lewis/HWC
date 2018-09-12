#ifndef __PARSE_TREE__PART_H__INCLUDED__
#define __PARSE_TREE__PART_H__INCLUDED__


typedef struct Parser_Part_Decl Parser_Part_Decl;
typedef struct Parser_Part_Stmt Parser_Part_Stmt;

typedef struct Parser_Type Parser_Type;


struct Parser_Part_Decl
{
	char *name;

	/* linked list, in reverse order of declaration */
	Parser_Part_Stmt *stmts;
};

struct Parser_Part_Stmt
{
	/* linked list, in reverse order of declaration */
	Parser_Part_Stmt *prev;

	Parser_Type *type;
	char        *name;
};


#endif

