#ifndef __PARSE_TREE__PLUGTYPE_H__INCLUDED__
#define __PARSE_TREE__PLUGTYPE_H__INCLUDED__


typedef struct PT_plugtype_decl  PT_plugtype_decl;

typedef struct PT_decl PT_decl;


struct PT_plugtype_decl
{
	char *name;
	// These should all be of type STMT_DECL
	PT_decl *fields;
};


// Debug functions

void dump_pt_plugtype_decl(PT_plugtype_decl *obj, int spaces);


#endif

