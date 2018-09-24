#ifndef __PARSE_TREE__PLUGTYPE_H__INCLUDED__
#define __PARSE_TREE__PLUGTYPE_H__INCLUDED__


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

void dump_plugtype_decl (PT_plugtype_decl  *obj, int spaces);
void dump_plugtype_field(PT_plugtype_field *obj, int spaces);


#endif

