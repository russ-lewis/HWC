#ifndef __FILE_RANGE_H__INCLUDED__
#define __FILE_RANGE_H__INCLUDED__


typedef struct FileRange FileRange;
struct FileRange
{
	struct {
		int l,c;   // line,col
	} s,e;             // start,end   (both inclusive)
};


#endif

