#ifndef __PARSE_TREE__FILE_H__INCLUDED__
#define __PARSE_TREE__FILE_H__INCLUDED__


typedef struct PT_file      PT_file;
typedef struct PT_file_decl PT_file_decl;

typedef struct PT_part_decl     PT_part_decl;
typedef struct PT_plugtype_decl PT_plugtype_decl;

static void dump_file(PT_file *, int);
static void dump_file_decl(PT_file_decl *, int);
static void dump_part_decl(PT_part_decl *, int);
static void dump_plugtype_decl(PT_plugtype_decl *, int);


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

// Debug functions

static void dump_file(PT_file *obj, int spaces)
{
	if(obj == NULL)
		return;

   int i;
   for(i = 0; i < spaces; i++)
      printf(" ");
   printf("File with the following decls: \n");
	dump_file_decl(obj->decls, spaces+2);
}

static void dump_file_decl(PT_file_decl *obj, int spaces)
{
	if(obj == NULL)
		return;

   int i;
   for(i = 0; i < spaces; i++)
      printf(" ");
   printf("File_decl with these decls: \n");
	dump_part_decl(obj->partDecl, spaces+2);
	dump_plugtype_decl(obj->plugtypeDecl, spaces+2);
	dump_file_decl(obj->prev, spaces);
}




#endif

