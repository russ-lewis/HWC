#include <stdio.h>

#include "names.h"
#include "part.h"
#include "stmt.h"



static void print_prefix(int cnt)
{
	char fmt[10];
	sprintf(fmt, "\%%%dc", cnt);
	printf((const char*)fmt, ' ');
}



char *enum2str(int mode)
{
	switch (mode)
	{
	case STMT_DECL:	       return "STMT_DECL";
	case STMT_BLOCK:       return "STMT_BLOCK";
	case STMT_CONN:        return "STMT_CONN";
	case STMT_FOR:         return "STMT_FOR";
	case STMT_IF:          return "STMT_IF";
	case STMT_ELSE:        return "STMT_ELSE";
	case STMT_ASRT:        return "STMT_ASRT";

	case EXPR_IDENT:       return "EXPR_IDENT";
	case EXPR_NUM:         return "EXPR_NUM";
	case EXPR_BOOL:        return "EXPR_BOOL";
	case EXPR_TWOOP:       return "EXPR_TWOOP";
	case EXPR_BITNOT:      return "EXPR_BITNOT";
	case EXPR_NOT:         return "EXPR_NOT";
	case EXPR_DOT:         return "EXPR_DOT";
	case EXPR_ARR:         return "EXPR_ARR_SLICE";
	case EXPR_ARR_SLICE:   return "EXPR_ARR_SLICE";
	case EXPR_PAREN:       return "EXPR_PAREN";
	case EXPR_BIT_TYPE:    return "EXPR_BIT_TYPE";

	case OP_EQUALS:        return "OP_EQUALS";
	case OP_NEQUAL:        return "OP_NEQUAL";
	case OP_BITAND:        return "OP_BITAND";
	case OP_AND:           return "OP_AND";
	case OP_BITOR:         return "OP_BITOR";
	case OP_OR:            return "OP_OR";
	case OP_XOR:           return "OP_XOR";
	case OP_LESS:          return "OP_LESS";
	case OP_GREATER:       return "OP_GREATER";
	case OP_LESSEQ:        return "OP_LESSEQ";
	case OP_GREATEREQ:     return "OP_GREATEREQ";
	case OP_PLUS:          return "OP_PLUS";
	case OP_MINUS:         return "OP_MINUS";
	case OP_TIMES:         return "OP_TIMES";
	case OP_DIVIDE:        return "OP_DIVIDE";
	case OP_MODULO:        return "OP_MODULO";
	}


	// this is a terrible design, in computer-science-purist perspective,
	// because it returns a static buffer.  But it's workable as a hackish
	// debug-only, never-used-in-parallel sort of situation.

	static char buf[256];
	sprintf(buf, "<Unrecognized enum %d>", mode);
	return buf;
}



void nameScope_dump(HWC_NameScope *names, int prefixLen)
{
	print_prefix(prefixLen);
	printf("--- NameScope ---\n");

	print_prefix(prefixLen);
	printf("refcount=%d\n", names->refCount);

	print_prefix(prefixLen);
	printf("parent=<TODO>\n");

	HWC_NameScope_elem *cur = names->list;
	if (cur == NULL)
	{
		print_prefix(prefixLen);
		printf("<no names>\n");
	}

	while (cur != NULL)
	{
		print_prefix(prefixLen+2);
		printf("name: %s\n", cur->name);

		if (cur->thing->file != NULL)
		{
printf("TODO: %s() marker 1\n", __func__);
		}

		if (cur->thing->part != NULL)
			part_dump(cur->thing->part, prefixLen+4);

		if (cur->thing->plugtype != NULL)
			plugtype_dump(cur->thing->plugtype, prefixLen+4);

		if (cur->thing->type != NULL)
		{
printf("TODO: %s() marker 3\n", __func__);
		}

		if (cur->thing->plug != NULL)
		{
printf("TODO: %s() marker 4\n", __func__);
		}

		if (cur->thing->decl != NULL)
			decl_dump(cur->thing->decl, prefixLen+4);

		cur = cur->next;
	}
}



void part_dump(HWC_Part *part, int prefixLen)
{
	print_prefix(prefixLen);
	printf("--- Part ---\n");

	if (part->fr.s.l == 0)
		printf("WARNING: This 'part' object does not have line number information!\n");

	print_prefix(prefixLen);
	printf("phases: begun %d completed %d\n", part->phases_begun, part->phases_completed);

	assert(part->publicNames != NULL);
	print_prefix(prefixLen);
	printf("publicNames:\n");
	nameScope_dump(part->publicNames, prefixLen+2);

	assert(part->privateNames != NULL);
	print_prefix(prefixLen);
	printf("privateNames:\n");
	nameScope_dump(part->privateNames, prefixLen+2);

	print_prefix(prefixLen);
	printf("stmts: len=%d\n", part->stmts_len);

	int i;
	for (i=0; i<part->stmts_len; i++)
	{
		print_prefix(prefixLen+2);
		printf("[%d]\n", i);

		if (part->stmts == NULL)
		{
			print_prefix(prefixLen+4);
			printf("<part->stmts is NULL>\n");
			continue;
		}

		stmt_dump(&part->stmts[i], prefixLen+4);
	}

	print_prefix(prefixLen);
	printf("decls: len=%d\n", part->decls_len);

	for (i=0; i<part->decls_len; i++)
	{
		print_prefix(prefixLen+2);
		printf("[%d]\n", i);

		if (part->decls == NULL)
		{
			print_prefix(prefixLen+4);
			printf("<part->decls is NULL>\n");
			continue;
		}

printf("TODO: %s() marker 5\n", __func__);
	}

	print_prefix(prefixLen);
	printf("size: %d\n", part->size);

	print_prefix(prefixLen);
	printf("numConn: %d\n", part->numConn);

	print_prefix(prefixLen);
	printf("numLogic: %d\n", part->numLogic);

	print_prefix(prefixLen);
	printf("numMemory: %d\n", part->numMemory);

	print_prefix(prefixLen);
	printf("numAssert: %d\n", part->numAssert);
}



void plugtype_dump(HWC_PlugType *plugtype, int prefixLen)
{
	print_prefix(prefixLen);
	printf("--- PlugType ---\n");

	if (plugtype->fr.s.l == 0)
		printf("WARNING: This 'plugtype' object does not have line number information!\n");

	print_prefix(prefixLen);
	printf("phases: begun %d completed %d\n", plugtype->phases_begun, plugtype->phases_completed);

	assert(plugtype->publicNames != NULL);
	print_prefix(prefixLen);
	printf("publicNames:\n");
	nameScope_dump(plugtype->publicNames, prefixLen+2);

	print_prefix(prefixLen);
	printf("decls: len=%d\n", plugtype->decls_len);

	int i;
	for (i=0; i<plugtype->decls_len; i++)
	{
		print_prefix(prefixLen+2);
		printf("[%d]\n", i);

		if (plugtype->decls == NULL)
		{
			print_prefix(prefixLen+4);
			printf("<plugtype->decls is NULL>\n");
			continue;
		}
	}

	print_prefix(prefixLen);
	printf("size: %d\n", plugtype->size);
}



void decl_dump(HWC_Decl *decl, int prefixLen)
{
	print_prefix(prefixLen);
	printf("--- Decl ---\n");

	if (decl->fr.s.l == 0)
		printf("WARNING: This 'decl' object does not have line number information!\n");

	print_prefix(prefixLen);
	printf("type: %s typeName: %s isMem: %d\n", 
	       enum2str(decl->type), decl->typeName, decl->isMem);

	if (decl->base_plugType != NULL)
	{
printf("TODO: %s() marker 6\n", __func__);
	}

	if (decl->base_part != NULL)
	{
printf("TODO: %s() marker 7\n", __func__);
	}

	print_prefix(prefixLen);
	printf("expr: <TODO>\n");

	if (decl->expr != NULL)
	{
printf("TODO: %s() marker 8\n", __func__);
	}

	print_prefix(prefixLen);
	printf("index: %d\n", decl->indexSize);
}



void stmt_dump(HWC_Stmt *stmt, int prefixLen)
{
	print_prefix(prefixLen);
	printf("--- Stmt ---\n");

	if (stmt->fr.s.l == 0)
		printf("WARNING: This 'stmt' object does not have line number information!\n");

	print_prefix(prefixLen);
	printf("mode: %s\n", enum2str(stmt->mode));

printf("TODO: %s() marker 9\n", __func__);
}


