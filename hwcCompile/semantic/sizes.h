#ifndef __SEMANTIC_SIZES_H__INCLUDED__
#define __SEMANTIC_SIZES_H__INCLUDED__


#include <stdio.h>
#include <memory.h>



/* HWC_Sizes
 *
 * This struct is used to store the sizes of various compnents (and later, the
 * offsets) of various resources; the meaning of each resource is described
 * inside the struct.
 *
 * Most objects (part and plugtype being the only exceptions) have two copies
 * of this struct, one named 'size' and the other named 'offset'.  The 'size'
 * field is the number of these resources consumed by the current object; it is
 * set entirely *independently* of any of the other objects around it.  (Note,
 * however, that the size must include all of the sizes of any objects nested
 * *inside* the current object.  For instance, a STMT_BLOCK will report a size
 * which reflects everything *inside* the block, but which entirely ignores
 * all other statements outside it.
 *
 * The 'offset' field gives the offset to the slot(s) which will be used by
 * this object, to store the resources that it must consume.  This offset is
 * relative to the enclosing object - which is typically a part or plugtype.
 * The offset fields are *always* set, even for objects that don't use any of
 * a particular part type; in that case, the next object will have the same
 * offset for that resource.
 *
 * For example, consider an object tree as follows:
 *    part X
 *        stmt 1 DECL
 *        stmt 2 CONN
 *        stmt 3 IF
 *            stmt 3.1-1 CONN
 *            stmt 3.1-2 CONN
 *          (else)
 *            stmt 3.2-1 CONN
 *        stmt 4 CONN
 *
 * We note that the statements 3.1-1, 3.1-2, and 3.2-1 are all nested inside
 * the IF statement (3).  Thus, the 'size' of 3 would include all of the
 * resources consumed by all 3 of the nested statements *PLUS* any consumed
 * by the IF itself (such as any logical operators used in the loop
 * condition).
 *
 * However, although the statements are nested, we do *NOT* view the nested
 * statements as "inside" the if() for the purposes of the offset calculation.
 * Instead, *all* of these statements give their offsets relative to the
 * *entire* part.  (This allows us to easily generate the wiring diagram.)
 *
 * However, see below for an exception: for() loops!
 *
 * GENERATING THE SIZE AND OFFSET TABLES
 *
 * We fill in both 'size' and 'offset' during phase 30.  We do so recursively.
 * We begin by setting all of the 'offset' fields, of the first object, to
 * zero by calling sizes_set_zero().  In the example above, we would start
 * with the first statement, namely the DECL (1).
 *
 * We then iterate through the objects in the table.  We first calculate the
 * size of the object, and then add the current object's size to its offset
 * to generate the offset of the next.
 *
 * When it is necessary to recurse (such as 3 recursing into 3.1-1), we
 * first calculate the local, non-recursive size, storing it into a temporary
 * variable.  (For an if statement, the non-recursive size reflects the
 * condition, and any logical operators that it requires.)  We then calculate
 * the offset of the first recursive element (in this example, 3.1-1) as the
 * offset of the enclosing element (3) plus the local size.  We then recurse
 * as necessary.  In the case of if(), where we have two different recursive
 * spaces, we arrange them consecutively; the offset of the first 'else'
 * statement follows immediately after the space of the last 'true' statement.
 *
 * Our last step, in a recursive case, is to update the 'size' of the
 * enclosing object, to include both its local and its recursive sizes.
 *
 * USING THE OFFSET TABLES
 *
 * The offset tables are used later on.  When it comes time to actually place
 * various objects into an array (say, placing Connection objects into the
 * wiring diagram), each object uses its own local 'offset' field (plus the
 * "overall position" of the part itself) to determine where to place the
 * elements.
 *
 * So, for instance, if a declaration has offset.bits==13, and the part that
 * it is inside of is at the position bits=129, then this declaration will
 * *actually* be placed at bits=142.
 *
 * FOR LOOPS - THE SPECIAL CASE
 *
 * We've stated above that the 'offset' fields (almost) always use the
 * enclosing part or plugtype as the "base" from which the offset is used.
 * We use this system because each statement, declaration, and expression
 * in a part or plugtype only occurs once per instantiation of the type;
 * however, each type might be instantiated many times.  Thus, in the
 * example above, we had offset.bits==13, with the part at bits=129; thus,
 * the declaration actually starts at bits=142.  But if there was *another*
 * instance of the same part, this time at bits=997, then there would be
 * another instance of the declaration, this time at bits=1010.
 *
 * This system works because (except with for() loops), each statement only
 * appears once per part; thus, part-relative offsets make sense.  However,
 * everything inside a for() loop appears multiple times within the part.
 *
 * Thus, a for() loop functions as a base for offsets - just like a part.
 * That is, the first statement inside a loop will start with offset 0 (for
 * all resources), and the various statements will consume space in much
 * the same way that they do inside a part.
 *
 * What, then, is the size of a for() statement?  It is the size of all of
 * the resources consumed by all passes of the loop: that is, the total
 * size of one pass of the loop, times the number of passes.
 *
 * When we are generating the wiring diagram for a loop, the generator
 * algorithm works basically like this:
 *    part_base = ...
 *    for i=0 to num_passes:
 *        offset_this_pass = part_base + for_loop_offset + i*size_per_pass
 *        build_statements(stmts, offset_this_pass)
 *
 * That is, the offset of the first pass is equal to the base of the part
 * itself, plus the offset of the for statement (since this offset is
 * relative to the part).  On each subsequent pass, the offset increments
 * by the size of one pass.
 *
 * If for() loops are nested, then, for the inner loops, replace "part base"
 * in the above discussion with "starting offset of the enclosing for()
 * loop".
 *
 * OTHER INTERFACE DETAILS
 *
 * When you create an HWC_Sizes object, call sizes_init() to initialize the
 * struct; this will set all of the fields to -1.  (You can call sizes_are_ready()
 * to check, later, to see if a HWC_Sizes struct has had all of its fields
 * set to reasonable values.)
 */



typedef struct HWC_Sizes HWC_Sizes;
struct HWC_Sizes
{
	/* ordinary bits: known as the "bit space" in the simulator.  These
	 * are the bits which represent inputs and outputs of parts, and the
	 * fields of plugs.
	 */
	int bits;

	/* memory bits: these are used to store the durable bits of the
	 * memory cells *outside* the main bit space.  Note that a memory
	 * plug, which uses a type with X bits, will consume 2*X bits in the
	 * ordinary space (first for the side which allows other components
	 * to read from the memory, and then for the side which allows them
	 * to write to the memory), while it consumes X bits in the memory
	 * space.
	 */
	int memBits;


	/* these reflect components which will be written to the wiring
	 * diagram.  Note that all counts are in terms of the number of
	 * *COMPONENTS*, never in terms of the number of bits used by those
	 * components.
	 */
	int conns, memoryObjs, logicOps, asserts;
};



static inline void sizes_init(HWC_Sizes *obj)
{
	memset(obj, -1, sizeof(*obj));
}

static inline void sizes_set_zero(HWC_Sizes *obj)
{
	memset(obj, 0, sizeof(*obj));
}

static inline int sizes_are_ready(HWC_Sizes *obj)
{
	if (obj == NULL)
		return 0;

	return obj->bits       >= 0 &&
	       obj->memBits    >= 0 &&
	       obj->conns      >= 0 &&
	       obj->memoryObjs >= 0 &&
	       obj->logicOps   >= 0 &&
	       obj->asserts    >= 0;
}

static inline void sizes_copy(HWC_Sizes *dst, HWC_Sizes *src)
{
	memcpy(dst,src, sizeof(*dst));
}

static inline void sizes_add(HWC_Sizes *dst,
                             HWC_Sizes *src1, HWC_Sizes *src2)
{
	assert(dst != NULL);
	assert(sizes_are_ready(src1));
	assert(sizes_are_ready(src2));

	dst->bits       = src1->bits       + src2->bits;
	dst->memBits    = src1->memBits    + src2->memBits;
	dst->conns      = src1->conns      + src2->conns;
	dst->memoryObjs = src1->memoryObjs + src2->memoryObjs;
	dst->logicOps   = src1->logicOps   + src2->logicOps;
	dst->asserts    = src1->asserts    + src2->asserts;
}

static inline void sizes_inc(HWC_Sizes *dst, HWC_Sizes *more)
{
	sizes_add(dst, dst,more);
}

static inline void sizes_multiply(HWC_Sizes *dst,
                                  HWC_Sizes *src, int factor)
{
	assert(dst != NULL);
	assert(sizes_are_ready(src));
	assert(factor > 0);           // TODO: will we allow 0 length arrays???

	dst->bits       = src->bits       * factor;
	dst->memBits    = src->memBits    * factor;
	dst->conns      = src->conns      * factor;
	dst->memoryObjs = src->memoryObjs * factor;
	dst->logicOps   = src->logicOps   * factor;
	dst->asserts    = src->asserts    * factor;
}

static inline void sizes_print(HWC_Sizes *obj)
{
	printf("bits=%d memBits=%d   conns=%d memoryObjs=%d logicOps=%d asserts=%d\n",
	       obj->bits, obj->memBits,
	       obj->conns, obj->memoryObjs, obj->logicOps, obj->asserts);
}



#endif

