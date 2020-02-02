#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "wiring/build.h"
#include "wiring/core.h"
#include "../hwcCompile/semantic/part.h"
#include "../hwcCompile/semantic/decl.h"
#include "../hwcCompile/semantic/stmt.h"
#include "../hwcCompile/semantic/expr.h"
#include <pt/expr.h>

// Prototypes, used later
int findPart     (HWC_Wiring *, HWC_Part *, int *, int *, int *, int *);
int findMemory   (HWC_Wiring_Memory     *, HWC_Part *, int);
int findLogicStmt(HWC_Wiring_Logic      *, HWC_Part *, int);
int findLogicExpr(HWC_Wiring_Logic      *, HWC_Expr *, int);
int findConnect  (HWC_Wiring_Connection *, HWC_Part *, int);
int findAssert   (HWC_Wiring_Assert     *, HWC_Part *, int);

// TODO: What should I put for debug in all of these?

// TODO: Header comments for, like, all of these.

// ASSUMPTION: The given part is the "main" part, and the numConn, numLogic etc. in the "main" part is equal to
//   the max number of conns, logics, etc. that the wiring diagram will need.
HWC_Wiring *buildWiringDiagram(HWC_Part *part)
{
	HWC_Wiring *retval = malloc(sizeof(HWC_Wiring));

	// Size
	retval->numBits = part->sizes.bits;

	// Memory
	retval->numMemRanges = part->sizes.memoryObjs;
	retval->mem = malloc(sizeof(HWC_Wiring_Memory) * part->sizes.memoryObjs);
	int memoryFound = 0;

	// Logic
	retval->numLogicalOperators = part->sizes.logicOps;
	retval->logic = malloc(sizeof(HWC_Wiring_Logic) * part->sizes.logicOps);
	int logicFound = 0;

	// Connections
	retval->numConnections = part->sizes.conns;
	retval->conns = malloc(sizeof(HWC_Wiring_Memory) * part->sizes.conns);
	int connectFound = 0;

	// Asserts
	retval->numAsserts = part->sizes.asserts;
	retval->asserts = malloc(sizeof(HWC_Wiring_Memory) * part->sizes.asserts);
	int assertFound = 0;

	findPart(retval, part, &memoryFound, &logicFound, &connectFound, &assertFound);

	assert(memoryFound  == part->sizes.memoryObjs);
	assert(logicFound   == part->sizes.logicOps);
	assert(connectFound == part->sizes.conns);
	assert(assertFound  == part->sizes.asserts);

	return retval;
}

// Other parts are found through decls, so we need to do this to find stmts and exprs in parts.
int findPart(HWC_Wiring *wiring, HWC_Part *part, int *indexMemory, int *indexLogic, int *indexConn, int *indexAssert)
{
	int i;
	HWC_Decl currDecl;
	for(i = 0; i < part->decls_len; i++)
	{
		currDecl = part->decls[i];

		if(currDecl.base_part != NULL)
			findPart(wiring, currDecl.base_part, indexMemory, indexLogic, indexConn, indexAssert);
	}

	*indexMemory = findMemory   (wiring->mem    , part, *indexMemory);
	*indexLogic  = findLogicStmt(wiring->logic  , part, *indexLogic);
	*indexConn   = findConnect  (wiring->conns  , part, *indexConn);
	*indexAssert = findAssert   (wiring->asserts, part, *indexAssert);

	return 0;
}

int findMemory(HWC_Wiring_Memory *memory, HWC_Part *part, int index)
{
	int i;
	HWC_Decl currDecl;
	for(i = 0; i < part->decls_len; i++)
	{
		currDecl = part->decls[i];

		if(currDecl.isMem == 1)
		{
			memory[index].size  = currDecl.sizes.bits;
			// TODO: What to put for these?
			memory[index].read  = currDecl.offsets.bits;
			memory[index].write = currDecl.offsets.bits + currDecl.sizes.bits/2;
			memory[index].debug = NULL;
			index++;
		}
	}
	return index;
}

int findLogicStmt(HWC_Wiring_Logic *logic, HWC_Part *part, int index)
{
	int i;
	HWC_Stmt currStmt;
	for(i = 0; i < part->stmts_len; i++)
	{
		currStmt = part->stmts[i];

		// TODO: Add code to do IF, FOR, and other BLOCK stmts.

		switch(currStmt.mode)
		{
			default:
				// NOP
				break;

			case STMT_CONN:
			case STMT_IF:
				index = findLogicExpr(logic, currStmt.exprA, index);
				index = findLogicExpr(logic, currStmt.exprB, index);
				break;

			case STMT_FOR:
			case STMT_ASRT:
				index = findLogicExpr(logic, currStmt.exprA, index);
				break;
		}
	}

	return index;
}


int findLogicExpr(HWC_Wiring_Logic *logic, HWC_Expr *expr, int index)
{
	int temp;

	switch(expr->mode)
	{
		default:
			break;

		case EXPR_NOT:
			logic[index].type = WIRING_NOT;
			logic[index].size = expr->sizes.bits;
			logic[index].a = expr->exprA->decl->offsets.bits;
			logic[index].out = expr->offsets.bits;
			logic[index].debug = NULL;
			index++;
			break;

		case EXPR_TWOOP:
			switch(expr->twoOp)
			{
				default:
					break;

				case OP_EQUALS:
					// TODO
					logic[index].type = WIRING_EQ;
					logic[index].size = expr->sizes.bits;
					logic[index].a    = expr->exprA->decl->offsets.bits;
					logic[index].b    = expr->exprB->decl->offsets.bits;
					logic[index].out  = expr->retvalSize;
					logic[index].debug = NULL;
					index++;
					break;

				case OP_NEQUAL:
				case OP_AND:
				case OP_OR:
				case OP_XOR:
					// TODO: Is there a better way to do this?
					if(expr->twoOp == OP_EQUALS)
						temp = WIRING_EQ;
					if(expr->twoOp == OP_NEQUAL)
						temp = WIRING_NEQ;
					if(expr->twoOp == OP_AND)
						temp = WIRING_AND;
					if(expr->twoOp == OP_OR)
						temp = WIRING_OR;
					if(expr->twoOp == OP_XOR)
						temp = WIRING_XOR;
					logic[index].type = temp;

					// TODO: Are these the correct values?
					logic[index].size = 2;
					logic[index].a = expr->exprA->decl->offsets.bits;
					logic[index].b = expr->exprB->decl->offsets.bits;
					logic[index].out = expr->offsets.bits;
					logic[index].debug = NULL;
					index++;
					break;
			}

		case EXPR_BITNOT:
		case EXPR_DOT:
			index = findLogicExpr(logic, expr->exprA, index);
			break;

		case EXPR_ARR:
		case EXPR_ARR_SLICE:
			index = findLogicExpr(logic, expr->exprA, index);
			index = findLogicExpr(logic, expr->exprB, index);
			break;
	}

	return index;
}

// TODO: Merge Connect and Assert into one function eventually? They both iterate over stmts after all.
int findConnect(HWC_Wiring_Connection *connect, HWC_Part *part, int index)
{
	int i;

	HWC_Stmt *currStmt;
	for(i = 0; i < part->stmts_len; i++)
	{
		currStmt = &part->stmts[i];

		// TODO: Add code to do IF, FOR, and other BLOCK stmts.
		// TODO: Remember, for conditionals, do WIRING_BIT_INVALID +1 or something

		switch(currStmt->mode)
		{
		default:
			assert(0);   // invalid statement type

		case STMT_DECL:
			break;    // NOP

		case STMT_CONN:
			connect[index].size = currStmt->exprA->retvalSize;
			connect[index].to   = currStmt->exprA->retvalOffset;
			connect[index].from = currStmt->exprB->retvalOffset;
			connect[index].condition = WIRING_BIT_INVALID;
			connect[index].isUndir = 1;
			connect[index].debug = NULL;
			index++;
			break;

		case STMT_IF:
			assert(0);
			break;

		case STMT_FOR:
			assert(0);
			break;

		case STMT_BLOCK:
			assert(0);
			break;

		case STMT_ASRT:
			break;    // NOP
		}
	}

	return index;
}


int findAssert(HWC_Wiring_Assert *assert, HWC_Part *part, int index)
{
	int i;
	HWC_Stmt *currStmt;
	for(i = 0; i < part->stmts_len; i++)
	{
		/* we ignore everything *except* for assert statements,
		 * in this function.
		 */
		if (part->stmts[i].mode != STMT_ASRT)
			continue;

		currStmt = &part->stmts[i];

		// Set the bit the assert reads
		assert[index].bit = currStmt->offsets.bits;
		index++;
	}

	return index;
}

/*
struct HWC_Wiring
{
	// how many bits are there in the entire system.  This is equal to the
	// size of the compiled 'main' part.  Of course, it includes bits for
	// all of the public plus, plus private plugs, plus all of the public
	// and private plugs of the many subcomponents - including implicit
	// plugs for every built-in logical component used in the entire
	// system.
	int numBits;

	// an array of HWC_Wiring_Memory objects.  Each object represents a
	// single contiguous range of memory cells; there are bit-indices for
	// both the read and write sides.
	int numMemRanges;
	HWC_Wiring_Memory *mem;

	// an array of HWC_Wiring_Logic objects.  Each object represents a
	// single logical operator, which can be over a single bit or over
	// many bits.
	int numLogicalOperators;
	HWC_Wiring_Logic *logic;

	// an array of HWC_Wiring_Connection objects.  Each object represents a
	// single connection, which might be over a single bit, or a range of
	// them.  Handles conditional and undirected connections as well.
	int numConnections;
	HWC_Wiring_Connection *conns;

	// an array of HWC_Wiring_Assert objects.  Each object represents a
	// single assertion, which always reads a single bit.
	int numAsserts;
	HWC_Wiring_Assert *asserts;
};


struct HWC_Wiring_Memory
{
	int size;     // how many bits?
	int read;     // index of 1st bit of the 'read' side
	int write;    // index of 1st bit of the 'write' side

	char *debug;
};


enum {
	WIRING_AND = 1,
	WIRING_OR,
	WIRING_XOR,
	WIRING_NOT,
	WIRING_EQ,
	WIRING_NEQ,
};
struct HWC_Wiring_Logic
{
	int type;     // use the enum above
	int size;
	int a,b;      // b is ignored for NOT, but used for all others
	int out;

	char *debug;
};


struct HWC_Wiring_Connection
{
	int size;     // how many bits?
	int to;       // index of 1st bit of the lhs of the assignment
	int from;     // index of 1st bit of the rhs of the assignment

	int condition;   // WIRING_BIT_INVALID if not conditional
	int isUndir;     // 1 if undirected; 0 if directed

	char *debug;
};


struct HWC_Wiring_Assert
{
	int bit;     // the bit to read

	char *debug;
};
*/
