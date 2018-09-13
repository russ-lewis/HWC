#ifndef __PARSE_TREE__PART_H__INCLUDED__
#define __PARSE_TREE__PART_H__INCLUDED__


typedef struct PT_part_decl PT_part_decl;
typedef struct PT_part_stmt PT_part_stmt;

typedef struct PT_type PT_type;
typedef struct PT_expr PT_expr;

typedef struct PT_array_decl PT_array_decl;


struct PT_part_decl
{
	char *name;

	/* linked list, in reverse order of declaration */
	PT_part_stmt *stmts;
};

struct PT_part_stmt
{
	/* linked list, in reverse order of declaration */
	PT_part_stmt *prev;

	PT_type *type;
	char        *name;
};



struct PT_array_decl
{
	PT_array_decl *prev;

	PT_expr *size;
};


#endif

