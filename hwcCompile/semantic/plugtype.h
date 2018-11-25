#ifndef __SEMANTIC_PLUGTYPE_H__INCLUDED__
#define __SEMANTIC_PLUGTYPE_H__INCLUDED__


// Maybe just want to reference "plug" struct instead?
typedef struct plugtype plugtype;
struct plugtype {

	// Temp variable and temp name until I have a better idea of what should go here.
	char wire;
};

// Presumably put primitive "bit" here
plugtype BIT;
BIT.wire = 0;


#endif // __SEMANTIC_PLUGTYPE_H__INCLUDEDED__
