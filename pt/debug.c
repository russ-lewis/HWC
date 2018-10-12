
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

	//dump_helper(spaces);
   //printf("Part_decl| named '%s', with part_stmts: \n", obj->name);
	//dump_part_stmt(obj->part_stmts, spaces+2);

	dump_helper(spaces);
	printf("Part_decl: named '%s', with stmts: \n", obj->name);
	dump_stmt(obj->stmts, spaces+2);
}

/*
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
*/

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
	//dump_plugtype_field(obj->fields, spaces+2);
	dump_decl(obj->fields, spaces+2);
}

/*
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
*/

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

		case STMT_DECL:
			printf("stmt: DECL, that is %s and has the decl vars:\n", obj->isPublic?"public":"private");
			dump_decl(obj->stmtDecl, spaces+2);
			break;

		case STMT_CONN:
			printf("stmt: CONNECTION, with left and right exprs:\n");
			dump_expr(obj->lHand, spaces+2);
			dump_expr(obj->rHand, spaces+2);
			break;

		case STMT_FOR:
			printf("stmt: FOR LOOP\n");
			dump_helper(spaces+2);
			printf("var: %s\n", obj->forVar);
			dump_helper(spaces+2);
			printf("Bgn:\n");
			dump_expr(obj->forBegin, spaces+4);
			dump_helper(spaces+2);
			printf("End=:\n");
			dump_expr(obj->forEnd, spaces+4);
			dump_helper(spaces+2);
			printf("Stmts:\n");
			dump_stmt(obj->forStmts, spaces+4);
			break;

		case STMT_IF:
			printf("stmt: IF CHECK\n");
			dump_expr(obj->ifExpr, spaces+2);
			dump_stmt(obj->ifStmts, spaces+2);
			break;

		case STMT_ELSE:
			printf("stmt: ELSE STMT\n");
			dump_stmt(obj->elseStmts, spaces+2);
			break;

		case STMT_ASRT:
			printf("stmt: ASSERTION\n");
			dump_expr(obj->assertion, spaces+2);
			break;

		
	}

}

void dump_decl(PT_decl *obj, int spaces)
{
	if(obj == NULL)
		return;

	// Call first since linked list is backwards
	dump_decl(obj->prev, spaces);

	dump_helper(spaces);

	// TODO: Add a debug statement for public/private
   printf("Declaration: named '%s', with type and array_decl\n", obj->name);
	dump_type(obj->type, spaces+2);
	dump_array_decl(obj->arraySuffix, spaces+2);
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
			printf("len = ");     // line 3
			dump_expr(obj->len, 0);
			break;

		case TYPE_IDENT:
			printf("type: IDENT, %s\n", obj->ident);
			break;
	}
}


// ---- DECLARED IN pt/expr.h ----

void dump_expr(PT_expr *obj, int spaces)
{
	if(obj == NULL)
		return;

	dump_helper(spaces);

	switch (obj->mode)
	{
		default:
			printf("-- debug: UNRECOGNIZED TYPE ---\n");
			break;

		case EXPR_IDENT:
			printf("Expr: IDENT, name = %s\n", obj->name);
			break;

		case EXPR_NUM:
			printf("Expr: NUM, value of %s\n", obj->num);
			break;

		case EXPR_EQUAL:
			printf("Expr: EQUAL, with exprs\n");
			dump_helper(spaces+2);
			printf("LHand:\n");
			dump_expr(obj->lHand, spaces+4);
			dump_helper(spaces+2);
			printf("RHand:\n");
			dump_expr(obj->rHand, spaces+4);
			break;
	}
}

