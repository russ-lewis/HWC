
#include "decl.h"


#include <stdio.h>
#include <malloc.h>
#include <assert.h>

/*
TODO: Changed header comment

Takes the given grammar PT_stmt and creates a corresponding semantic HWC_Stmt from it.
The most notable changes are:
 - Conversion from linked list structure to array
 - Compression of struct fields
 - malloc()s memory for the caller
Arguments:
 - input, a pointer to the statement to convert
 - output, a pointer to the HWC_Stmt to fill in
 - caller, 
***NOTE: Could remove output parameter, because caller contains output (see function call in phase10_part.c)
Returns an int corresponding to the length of the array of statements
*/
int convertPTstmtIntoHWCdecl(PT_decl *input, HWC_Decl *output)
{
	PT_decl *currPTdecl = input;

	struct PT_decl
	{
   /* linked list, in reverse order of declaration */
   PT_decl *prev;

   PT_type *type;
   char *name;
   PT_array_decl *arraySuffix;
	};



	/*
	int len = 0;
	while(currPTstmt != NULL)
	{
		currPTstmt = currPTstmt->prev;
		len++;
	}

	output = malloc(sizeof(HWC_Stmt)*len);
	if(output == NULL)
	{
		assert(0); // TODO: Better error message?
	}
	*/

	return 0;
}
