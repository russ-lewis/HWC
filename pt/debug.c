
/* this grabs all of the parse tree types and declarations */

#include <stdio.h>

#include "all.h"



// Returns 0 on success
// Returns 1 if obj is NULL
static int dump_helper(void *obj, int spaces)
{
	// May be redundant
	if(obj == NULL)
		return 1;

	int i;
	for(i = 0; i < spaces; i++)
		printf(" ");
	return 0;
}



// ---- DECLARED IN pt/file.h ----

void dump_file(PT_file *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("File with the following decls: \n");
	dump_file_decl(obj->decls, spaces+2);
}

void dump_file_decl(PT_file_decl *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("File_decl with these decls: \n");
	dump_part_decl(obj->partDecl, spaces+2);
	dump_plugtype_decl(obj->plugtypeDecl, spaces+2);
	dump_file_decl(obj->prev, spaces);
}



// ---- DECLARED IN pt/part.h ----

void dump_part_decl(PT_part_decl *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("Part_decl: named '%s', with part_stmts: \n", obj->name);
	dump_part_stmt(obj->stmts, spaces+2);
}

void dump_part_stmt(PT_part_stmt *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("Part_stmt: named '%s', %s with type:\n", obj->name, obj->isPub?"public":"private");
	dump_type(obj->type, spaces+2);
	dump_part_stmt(obj->prev, spaces);
}


void dump_array_decl(PT_array_decl *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("Array_decl: Size of\n");
	dump_expr(obj->size, spaces+2);
	dump_array_decl(obj->prev, spaces);
}



// ---- DECLARED IN pt/plugtype.h ----

void dump_plugtype_decl(PT_plugtype_decl *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("Plugtype_decl: named '%s', with fields\n", obj->name);
	dump_plugtype_field(obj->fields, spaces+2);
}

void dump_plugtype_field(PT_plugtype_field *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("Plugtype_field: named '%s', with type and array_decl\n", obj->name);
	dump_type(obj->type, spaces+2);
	dump_array_decl(obj->arraySuffix, spaces+2);
	dump_plugtype_field(obj->prev, spaces);
}



// ---- DECLARED IN pt/type.h ----

void dump_type(PT_type *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1) 
		return;

	switch (obj->mode)
	{
	default:
		printf("-- debug: UNRECOGNIZED TYPE ---\n");
		break;

	case TYPE_BIT:
		printf("type: BIT\n");
		break;

	case TYPE_ARRAY:
		printf("type: ARRAY\n");          // line 1

		dump_type(obj->base, spaces+2);   // line 2

		dump_helper(obj,spaces);
		printf("len = %s\n", obj->len);   // line 3
		break;

	case TYPE_IDENT:
		printf("type: IDENT, %s\n", obj->ident);
	}
}



// ---- DECLARED IN pt/expr.h ----

void dump_expr(PT_expr *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

	printf("Expr: named '%s', mode = %d\n", obj->name, obj->mode);
}

