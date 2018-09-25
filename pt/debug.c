
/* this grabs all of the parse tree types and declarations */

#include <stdio.h>

#include "all.h"



// Returns 0 on success
// Returns 1 if obj is NULL
static void dump_helper(int spaces)
{
	int i;
	for(i = 0; i < spaces; i++)
		printf(" ");
}



// ---- DECLARED IN pt/file.h ----

void dump_file(PT_file *obj, int spaces)
{
	if(obj == NULL)
		return;

	dump_helper(spaces);

   printf("File with the following decls: \n");
	dump_file_decl(obj->decls, spaces+2);
}

void dump_file_decl(PT_file_decl *obj, int spaces)
{
	if(obj == NULL)
		return;

	// Call first since linked list is backwards
	dump_file_decl(obj->prev, spaces);

	dump_helper(spaces);

   printf("File_decl with these decls: \n");
	dump_part_decl(obj->partDecl, spaces+2);
	dump_plugtype_decl(obj->plugtypeDecl, spaces+2);
}



// ---- DECLARED IN pt/part.h ----

void dump_part_decl(PT_part_decl *obj, int spaces)
{
	if(obj == NULL)
		return;

	dump_helper(spaces);

   printf("Part_decl: named '%s', with part_stmts: \n", obj->name);
	dump_part_stmt(obj->part_stmts, spaces+2);
	printf("         : named '%s', with stmts: \n", obj->name);
	dump_stmt(obj->stmts, spaces+2);
}

void dump_part_stmt(PT_part_stmt *obj, int spaces)
{
	if(obj == NULL)
		return;

	// Call first since linked list is backwards
	dump_part_stmt(obj->prev, spaces);

	dump_helper(spaces);

   printf("Part_stmt: named '%s', %s with type:\n", obj->name, obj->isPub?"public":"private");
	dump_type(obj->type, spaces+2);
}


void dump_array_decl(PT_array_decl *obj, int spaces)
{
	if(obj == NULL)
		return;

	// Call first since linked list is backwards
	dump_array_decl(obj->prev, spaces);

	dump_helper(spaces);

   printf("Array_decl: Size of\n");
	dump_expr(obj->size, spaces+2);
}



// ---- DECLARED IN pt/plugtype.h ----

void dump_plugtype_decl(PT_plugtype_decl *obj, int spaces)
{
	if(obj == NULL)
		return;

	dump_helper(spaces);

   printf("Plugtype_decl: named '%s', with fields\n", obj->name);
	dump_plugtype_field(obj->fields, spaces+2);
}

void dump_plugtype_field(PT_plugtype_field *obj, int spaces)
{
	if(obj == NULL)
		return;

	// Call first since linked list is backwards
	dump_plugtype_field(obj->prev, spaces);

	dump_helper(spaces);

   printf("Plugtype_field: named '%s', with type and array_decl\n", obj->name);
	dump_type(obj->type, spaces+2);
	dump_array_decl(obj->arraySuffix, spaces+2);
}


// ---- DECLARED IN pt/stmt.h ----

void dump_stmt(PT_stmt *obj, int spaces)
{
	if(obj == NULL)
		return;

	dump_stmt(obj->prev, spaces);

	dump_helper(spaces);

	switch (obj->mode)
	{
		default:
			printf("-- debug: UNRECOGNIZED STMT ---\n");
			break;

		case STMT_CONN:
			printf("stmt: CONNECTION\n");
			break;

		case STMT_FOR:
			printf("stmt: FOR LOOP\n");
			break;

		case STMT_IF:
			printf("stmt: IF CHECK\n");
	}

}


// ---- DECLARED IN pt/type.h ----

void dump_type(PT_type *obj, int spaces)
{
	if(obj == NULL)
		return;

	dump_helper(spaces);

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

		dump_helper(spaces);
		printf("len = %s\n", obj->len);   // line 3
		break;

	case TYPE_IDENT:
		printf("type: IDENT, %s\n", obj->ident);
	}
}



// ---- DECLARED IN pt/expr.h ----

void dump_expr(PT_expr *obj, int spaces)
{
	if(obj == NULL)
		return;

	dump_helper(spaces);

	printf("Expr: named '%s', mode = %d\n", obj->name, obj->mode);
}

