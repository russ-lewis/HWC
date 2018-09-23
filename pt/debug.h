#pragma once

/*





*/

typedef struct PT_expr      PT_expr;
typedef struct PT_file      PT_file;
typedef struct PT_file_decl PT_file_decl;
typedef struct PT_part_decl PT_part_decl;
typedef struct PT_part_stmt PT_part_stmt;
typedef struct PT_array_decl PT_array_decl;
typedef struct PT_plugtype_decl  PT_plugtype_decl;
typedef struct PT_plugtype_field PT_plugtype_field;
typedef struct PT_type      PT_type;


// Expr
static void dump_expr(PT_expr *, int);
// File
static void dump_file(PT_file *, int);
static void dump_file_decl(PT_file_decl *, int);
// Part
static void dump_part_decl (PT_part_decl  *, int);
static void dump_part_stmt (PT_part_stmt  *, int);
static void dump_array_decl(PT_array_decl *, int);
// Plugtype
static void dump_plugtype_decl (PT_plugtype_decl  *, int);
static void dump_plugtype_field(PT_plugtype_field *, int);
// Type
static void dump_type(PT_type *, int spaces);


// Returns 0 on success
// Returns 1 if obj is NULL
static int dump_helper(void *obj, int spaces)
{
	// May be redundant
	if(obj == NULL)
		return 1;

	int i;
	for(i = 0; i < spaces; i++)
		printf(" ");
	return 0;
}
