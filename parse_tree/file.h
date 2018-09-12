#ifndef __PARSE_TREE__FILE_H__INCLUDED__
#define __PARSE_TREE__FILE_H__INCLUDED__


typedef struct Parser_File      Parser_File;
typedef struct Parser_File_Decl Parser_File_Decl;

typedef struct Parser_Part_Decl     Parser_Part_Decl;
typedef struct Parser_Plugtype_Decl Parser_Plugtype_Decl;


struct Parser_File
{
	/* linked list of declarations, in reverse order */
	Parser_File_Decl *decls;
};

struct Parser_File_Decl
{
	/* linked list of declarations, in reverse order */
	Parser_File_Decl *prev;

	Parser_Part_Decl     *partDecl;
	Parser_Plugtype_Decl *plugtypeDecl;
};



#endif

