
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

void dump_pt_file(PT_file *obj, int spaces)
{
	if(obj == NULL)
		return;

	dump_helper(spaces);

   printf("File with the following decls: \n");
	dump_pt_file_decl(obj->decls, spaces+2);
}

void dump_pt_file_decl(PT_file_decl *obj, int spaces)
{
	if(obj == NULL)
		return;

	PT_file_decl *cur = obj;
	while (cur != NULL)
	{
		dump_helper(spaces);

		printf("File_decl with these decls: \n");
		dump_pt_part_decl(cur->partDecl, spaces+2);
		dump_pt_plugtype_decl(cur->plugtypeDecl, spaces+2);

		cur = cur->next;
	}
}



// ---- DECLARED IN pt/part.h ----

void dump_pt_part_decl(PT_part_decl *obj, int spaces)
{
	if(obj == NULL)
		return;

	dump_helper(spaces);
	printf("Part_decl: named '%s', with stmts: \n", obj->name);
	dump_pt_stmt(obj->stmts, spaces+2);
}


// ---- DECLARED IN pt/plugtype.h ----

void dump_pt_plugtype_decl(PT_plugtype_decl *obj, int spaces)
{
	if(obj == NULL)
		return;

	dump_helper(spaces);

   printf("Plugtype_decl: named '%s', with fields\n", obj->name);
	dump_pt_stmt(obj->stmts, spaces+2);
}


// ---- DECLARED IN pt/stmt.h ----

void dump_pt_stmt(PT_stmt *obj, int spaces)
{
	if(obj == NULL)
		return;

	if (obj->fr.s.l == 0)
		printf("WARNING: This 'stmt' object does not have line number information!\n");

	PT_stmt *cur = obj;
	while (cur != NULL)
	{
		dump_helper(spaces);

		switch (cur->mode)
		{
		default:
			printf("-- debug: UNRECOGNIZED STMT ---\n");
			break;

		case STMT_DECL:
			printf("stmt: DECL:\n");

			dump_helper(spaces+2);
			printf("type:\n");

			dump_pt_expr(obj->declType, spaces+4);

			dump_helper(spaces+2);
			printf("prefix=");
			switch(cur->declPrefix)
			{
			default:
				assert(0);    // invalid value!

			case DECL_PREFIX_NOTHING:
				printf("n/a\n");
				break;

			case DECL_PREFIX_PUBLIC:
				printf("public\n");
				break;

			case DECL_PREFIX_PRIVATE:
				printf("private\n");
				break;

			case DECL_PREFIX_SUBPART:
				printf("subpart\n");
				break;
			}

			dump_helper(spaces+2);
			printf("isMemory=%d\n", cur->isMemory);

			dump_pt_decl(cur->declList, spaces+2);
			break;

		case STMT_BLOCK:
			printf("stmt: BLOCK, that has stmts...\n");
			dump_pt_stmt(cur->stmts, spaces+2);
			break;

		case STMT_CONN:
			printf("stmt: CONNECTION, with left and right exprs:\n");
			dump_pt_expr(cur->lHand, spaces+2);
			dump_pt_expr(cur->rHand, spaces+2);
			break;

		case STMT_FOR:
			printf("stmt: FOR LOOP\n");
			dump_helper(spaces+2);
			printf("var: %s\n", cur->forVar);
			dump_helper(spaces+2);
			printf("Bgn:\n");
			dump_pt_expr(cur->forBegin, spaces+4);
			dump_helper(spaces+2);
			printf("End=:\n");
			dump_pt_expr(cur->forEnd, spaces+4);
			dump_helper(spaces+2);
			printf("Stmts:\n");
			dump_pt_stmt(cur->forStmts, spaces+4);
			break;

		case STMT_IF:
			printf("stmt: IF CHECK\n");
			dump_pt_expr(cur->ifExpr, spaces+2);
			dump_pt_stmt(cur->ifStmts, spaces+2);
			break;

		case STMT_ASRT:
			printf("stmt: ASSERTION\n");
			dump_pt_expr(cur->assertion, spaces+2);
			break;
		}

		cur = cur->next;
	}
}

void dump_pt_decl(PT_decl *obj, int spaces)
{
	if(obj == NULL)
		return;

	if (obj->fr.s.l == 0)
		printf("WARNING: This 'decl' object does not have line number information!\n");

	PT_decl *cur = obj;
	while (cur != NULL)
	{
		dump_helper(spaces);
		printf("name: %s\n", cur->name);

		if (cur->init != NULL)
		{
			dump_helper(spaces+2);
			printf("MARKER: TODO: pt_decl init expression\n");
		}

		cur = cur->next;
	}
}


// ---- DECLARED IN pt/expr.h ----

void dump_pt_expr(PT_expr *obj, int spaces)
{
	if(obj == NULL)
		return;

	if (obj->fr.s.l == 0)
		printf("WARNING: This 'expr' object does not have line number information!\n");

	dump_helper(spaces);

	switch (obj->mode)
	{
		default:
			printf("--- debug: UNRECOGNIZED EXPR ---\n");
			break;

		case EXPR_IDENT:
			printf("Expr: IDENT, name = %s\n", obj->name);
			break;

		case EXPR_NUM:
			printf("Expr: NUM, value of %s\n", obj->num);
			break;

		case EXPR_BOOL:
			printf("Expr: BOOL, value of %d\n", obj->value);
			break;

		case EXPR_TWOOP:
			printf("Expr: TWOOP of mode");
			// Is there a way to compress this code?
			switch (obj->opMode)
			{
				default:
					printf("\n-- debug: UNRECOGNIZED TWO OP EXPR ---\n");
					break;
				case OP_EQUALS:
					printf(" EQUALS ");
					break;
				case OP_NEQUAL:
					printf(" NEQUAL ");
					break;
				case OP_LESS:
					printf(" LESS THAN ");
					break;
				case OP_GREATER:
					printf(" GREATER THAN ");
					break;
				case OP_LESSEQ:
					printf(" LESS THAN OR EQUAL TO ");
					break;
				case OP_GREATEREQ:
					printf(" GREATER THAN OR EQUAL TO ");
					break;
				case OP_BITAND:
					printf(" BITWISE AND ");
					break;
				case OP_AND:
					printf(" AND ");
					break;
				case OP_BITOR:
					printf(" BITWISE OR ");
					break;
				case OP_OR:
					printf(" OR ");
					break;
				case OP_XOR:
					printf(" XOR ");
					break;
				case OP_PLUS:
					printf(" PLUS ");
					break;
				case OP_MINUS:
					printf(" MINUS ");
					break;
				case OP_TIMES:
					printf(" TIMES ");
					break;
				case OP_DIVIDE:
					printf(" DIVIDE ");
					break;
				case OP_MODULO:
					printf(" MODULO ");
					break;
				case OP_CONCAT:
					printf(" CONCAT ");
					break;
			}
			printf("with exprs\n");
			dump_helper(spaces+2);
			printf("LHand:\n");
			dump_pt_expr(obj->lHand, spaces+4);
			dump_helper(spaces+2);
			printf("RHand:\n");
			dump_pt_expr(obj->rHand, spaces+4);
			break;

		case EXPR_BITNOT:
			printf("Expr: BITWISE NOT, with expr\n");
			dump_pt_expr(obj->notExpr, spaces+2);
			break;

		case EXPR_NOT:
			printf("Expr: NOT, with expr\n");
			dump_pt_expr(obj->notExpr, spaces+2);
			break;

		case EXPR_DOT:
			printf("Expr: DOT, using expr\n");
			dump_pt_expr(obj->dotExpr, spaces+2);
			dump_helper(spaces);
			printf(" accessing field '%s'\n", obj->field);
			break;

		case EXPR_ARR:
			printf("Expr: ARR, into array expr\n");
			dump_pt_expr(obj->arrayExpr, spaces+2);
			dump_helper(spaces);
			printf(" index of\n");
			dump_pt_expr(obj->indexExpr, spaces+2);
			break;

		case EXPR_ARR_SLICE:
			printf("Expr: ARR_SLICE, into array expr\n");
			dump_pt_expr(obj->arrayExpr, spaces+2);
			dump_helper(spaces);
			printf(" lower bound\n");

			if (obj->indexExpr1 == NULL)
			{
				dump_helper(spaces+2);
				printf("-- none --\n");
			}
			else
				dump_pt_expr(obj->indexExpr1, spaces+2);

			dump_helper(spaces);
			printf(" upper bound\n");

			if (obj->indexExpr2 == NULL)
			{
				dump_helper(spaces+2);
				printf("-- none --\n");
			}
			else
				dump_pt_expr(obj->indexExpr2, spaces+2);

			break;

		case EXPR_BIT_TYPE:
			printf("\"bit\"\n");
			break;
	}
}

