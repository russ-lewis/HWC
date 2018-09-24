#ifndef __PARSE_TREE__PLUGTYPE_H__INCLUDED__
#define __PARSE_TREE__PLUGTYPE_H__INCLUDED__

#include "debug.h"

typedef struct PT_plugtype_decl  PT_plugtype_decl;
typedef struct PT_plugtype_field PT_plugtype_field;

typedef struct PT_array_decl PT_array_decl;   // actually defined in part.h


struct PT_plugtype_decl
{
	char *name;
	PT_plugtype_field *fields;
};

struct PT_plugtype_field
{
	PT_plugtype_field *prev;

	PT_type *type;
	char *name;
	PT_array_decl *arraySuffix;
};

// Debug functions

static void dump_plugtype_decl(PT_plugtype_decl *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("Plugtype_decl: named '%s', with fields\n", obj->name);
	dump_plugtype_field(obj->fields, spaces+2);
}

static void dump_plugtype_field(PT_plugtype_field *obj, int spaces)
{
	if(dump_helper(obj, spaces) == 1)
		return;

   printf("Plugtype_field: named '%s', with type and array_decl\n", obj->name);
	dump_type(obj->type, spaces+2);
	dump_array_decl(obj->arraySuffix, spaces+2);
	dump_plugtype_field(obj->prev, spaces);
}


#endif

