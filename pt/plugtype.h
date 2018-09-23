#ifndef __PARSE_TREE__PLUGTYPE_H__INCLUDED__
#define __PARSE_TREE__PLUGTYPE_H__INCLUDED__


typedef struct PT_plugtype_decl  PT_plugtype_decl;
typedef struct PT_plugtype_field PT_plugtype_field;

typedef struct PT_array_decl PT_array_decl;   // actually defined in part.h

static void dump_plugtype_decl (PT_plugtype_decl  *, int);
static void dump_plugtype_field(PT_plugtype_field *, int);
static void dump_type(PT_type *, int);
static void dump_array_decl(PT_array_decl *, int);

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
   if(obj == NULL)
      return;

   int i;
   for(i = 0; i < spaces; i++)
      printf(" ");
   printf("Plugtype_decl: %s, with fields\n", obj->name);
	dump_plugtype_field(obj->fields, spaces+2);
}

static void dump_plugtype_field(PT_plugtype_field *obj, int spaces)
{
   if(obj == NULL)
      return;

   int i;
   for(i = 0; i < spaces; i++)
      printf(" ");
   printf("Plugtype_field: %s, with type and array_decl\n", obj->name);
	dump_type(obj->type, spaces+2);
	dump_array_decl(obj->arraySuffix, spaces+2);
	dump_plugtype_field(obj->prev, spaces);
}


#endif

