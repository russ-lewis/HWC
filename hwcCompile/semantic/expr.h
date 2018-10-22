#ifndef __SEMANTIC_EXPR_H__INCLUDED__
#define __SEMANTIC_EXPR_H__INCLUDED__


#include "plug.h"
#include "partinstance.h"


#include <pt/expr.h>    // we'll re-use the modes from the parser, but then
                        // add some more

enum {
	EXPR_PLUG = EXPR__LAST_PARSER_MODE+1,
	EXPR_SUBCOMPONENT,
};


typedef struct HWC_Expr HWC_Expr;
struct HWC_Expr
{
	int mode;

	/* EXPR_PLUG */
	HWC_Plug *plug;

	/* EXPR_SUBCOMPONENT */
	HWC_PartInstance *subcomponent;
};


#endif

