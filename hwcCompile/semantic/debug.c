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
printf("TODO: line %d\n", __LINE__);
		}

		if (cur->thing->part != NULL)
			part_dump(cur->thing->part, prefixLen+4);

		if (cur->thing->plugtype != NULL)
		{
printf("TODO: line %d\n", __LINE__);
		}

		if (cur->thing->type != NULL)
		{
printf("TODO: line %d\n", __LINE__);
		}

		if (cur->thing->plug != NULL)
		{
printf("TODO: line %d\n", __LINE__);
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

	print_prefix(prefixLen);
	printf("phases: begun %d completed %d\n", part->phases_begun, part->phases_completed);

	print_prefix(prefixLen);
	printf("publicNames: <TODO>\n");

	if (part->publicNames != NULL)
		nameScope_dump(part->publicNames, prefixLen+2);

	print_prefix(prefixLen);
	printf("privateNames: <TODO>\n");

	if (part->privateNames != NULL)
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

printf("TODO: line %d\n", __LINE__);
	}

}



void decl_dump(HWC_Decl *decl, int prefixLen)
{
	print_prefix(prefixLen);
	printf("--- Decl ---\n");

	print_prefix(prefixLen);
	printf("type: %d typeName: %s isMem: %d\n", decl->type, decl->typeName, decl->isMem);

	if (decl->base_plugType != NULL)
	{
printf("TODO: line %d\n", __LINE__);
	}

	if (decl->base_part != NULL)
	{
printf("TODO: line %d\n", __LINE__);
	}

	print_prefix(prefixLen);
	printf("expr: <TODO>\n");

	if (decl->expr != NULL)
	{
printf("TODO: line %d\n", __LINE__);
	}

	print_prefix(prefixLen);
	printf("index: %d\n", decl->index);
}



char *stmt_mode2str(int mode)
{
	switch (mode)
	{
	case STMT_DECL:		return "STMT_DECL";
	case STMT_BLOCK:	return "STMT_BLOCK";
	case STMT_CONN:		return "STMT_CONN";
	case STMT_FOR:		return "STMT_FOR";
	case STMT_IF:		return "STMT_IF";
	case STMT_ELSE:		return "STMT_ELSE";
	case STMT_ASRT:		return "STMT_ASRT";
	}


	// this is a terrible design, in computer-science-purist perspective,
	// because it returns a static buffer.  But it's workable as a hackish
	// debug-only, never-used-in-parallel sort of situation.

	static char buf[256];
	sprintf(buf, "ERROR: Unrecognized stmt->mode %d\n", mode);
	return buf;
}

void stmt_dump(HWC_Stmt *stmt, int prefixLen)
{
	print_prefix(prefixLen);
	printf("--- Stmt ---\n");

	print_prefix(prefixLen);
	printf("mode: %s\n", stmt_mode2str(stmt->mode));

printf("TODO: line %d\n", __LINE__);
}


