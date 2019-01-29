#include <stdio.h>

#include "names.h"
#include "part.h"



static void print_prefix(int cnt)
{
	char fmt[10];
	sprintf(fmt, "\%%%dc", cnt);
	printf((const char*)fmt, ' ');
}



void nameScope_dump(HWC_NameScope *names, int prefixLen)
{
	print_prefix(prefixLen);
	printf("--- NameScope %p ---\n", names);

	print_prefix(prefixLen);
	printf("refcount=%d\n", names->refCount);

	print_prefix(prefixLen);
	printf("parent=%p\n", names->parent);

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

		print_prefix(prefixLen+2);
		printf("type: file %p part %p plugtype %p type %p plug %p decl %p\n",
		       cur->thing->file,
		       cur->thing->part,
		       cur->thing->plugtype,
		       cur->thing->type,
		       cur->thing->plug,
		       cur->thing->decl);

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
	printf("--- Part %p ---\n", part);

	print_prefix(prefixLen);
	printf("phases: begun %d completed %d\n", part->phases_begun, part->phases_completed);

	print_prefix(prefixLen);
	printf("publicNames: %p\n", part->publicNames);

	if (part->publicNames != NULL)
		nameScope_dump(part->publicNames, prefixLen+2);

	print_prefix(prefixLen);
	printf("privateNames: %p\n", part->privateNames);

	if (part->privateNames != NULL)
		nameScope_dump(part->privateNames, prefixLen+2);

	print_prefix(prefixLen);
	printf("stmts: len=%d\n", part->stmts_len);

	int i;
	for (i=0; i<part->stmts_len; i++)
	{
		print_prefix(prefixLen+2);
		printf("[%d]\n", i);

printf("TODO: line %d\n", __LINE__);
	}

	print_prefix(prefixLen);
	printf("decls: len=%d\n", part->decls_len);

	for (i=0; i<part->decls_len; i++)
	{
		print_prefix(prefixLen+2);
		printf("[%d]\n", i);

printf("TODO: line %d\n", __LINE__);
	}

}



void decl_dump(HWC_Decl *decl, int prefixLen)
{
	print_prefix(prefixLen);
	printf("--- Decl %p ---\n", decl);

	print_prefix(prefixLen);
	printf("type: %d typeName: %s\n", decl->type, decl->typeName);

	print_prefix(prefixLen);
	printf("base: plugtype %p part %p\n", decl->base_plugType, decl->base_part);

	if (decl->base_plugType != NULL)
	{
printf("TODO: line %d\n", __LINE__);
	}

	if (decl->base_part != NULL)
	{
printf("TODO: line %d\n", __LINE__);
	}

	print_prefix(prefixLen);
	printf("expr: %p\n", decl->expr);

	if (decl->expr != NULL)
	{
printf("TODO: line %d\n", __LINE__);
	}

	print_prefix(prefixLen);
	printf("index: %d\n", decl->index);
}


