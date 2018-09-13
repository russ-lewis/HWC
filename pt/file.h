#ifndef __PARSE_TREE__FILE_H__INCLUDED__
#define __PARSE_TREE__FILE_H__INCLUDED__


typedef struct PT_file      PT_file;
typedef struct PT_file_decl PT_file_decl;

typedef struct PT_part_decl     PT_part_decl;
typedef struct PT_plugtype_decl PT_plugtype_decl;


struct PT_file
{
	/* linked list of declarations, in reverse order */
	PT_file_decl *decls;
};

struct PT_file_decl
{
	/* linked list of declarations, in reverse order */
	PT_file_decl *prev;

	PT_part_decl     *partDecl;
	PT_plugtype_decl *plugtypeDecl;
};



#endif

