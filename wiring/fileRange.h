#ifndef __FILE_RANGE_H__INCLUDED__
#define __FILE_RANGE_H__INCLUDED__


#include <string.h>
#include <assert.h>


typedef struct FileRange FileRange;
struct FileRange
{
	char *filename;

	struct {
		int l,c;   // line,col
	} s,e;             // start,end   (both inclusive)
};



static inline int fr_valid(FileRange *fr)
{
	return fr->filename != NULL;
}

static inline void fr_copy(FileRange *dst, FileRange *src)
{
	assert(fr_valid(src));
	memcpy(dst,src, sizeof(*dst));
}

// TODO: do we need a 'join' operation?  Should it have mandatory overlap
//       semantics, maybe with an assert() to check?


#endif

