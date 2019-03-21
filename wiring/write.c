#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <ctype.h>

#include "core.h"
#include "write.h"



static void print_debug(FILE *fp, char *debug);

int wiring_write(HWC_Wiring *core, FILE *fp)
{
	if (fp == NULL)
	{
		fprintf(stderr, "ERROR: %s: The fp was NULL!\n", __func__);
		return 1;
	}


	int i;

	/* a little header, to make things obvious for a user.  It also
	 * supposes that we might, in the future, be well-known enough to
	 * be supported by 'file.'  Is that arrogant?
	 */
	fprintf(fp, "# HWC Wiring Diagram\n");

	/* support for future versions, just in case */
	fprintf(fp, "version: 1.0\n");
	fprintf(fp, "\n");

	/* TODO: put the file name here */
	fprintf(fp, "debug=\"\"\n");
	fprintf(fp, "\n");

	fprintf(fp, "bits %d\n", core->numBits);
	fprintf(fp, "\n");

	fprintf(fp, "memory count %d\n", core->numMemRanges);
	for (i=0; i<core->numMemRanges; i++)
	{
		fprintf(fp, "  memory size %d read %d write %d",
		            core->mem[i].size,
		            core->mem[i].read, core->mem[i].write);

		print_debug(fp, core->mem[i].debug);
	}
	fprintf(fp, "\n");


	fprintf(fp, "logic count %d\n", core->numLogicalOperators);
	for (i=0; i<core->numLogicalOperators; i++)
	{
		char *name;
		int binary = 1; // default value; changed by NOT

		// why use this switch instead of a lookup table?  For
		// better sanity-checking that the values line up.  Maybe
		// we'll optimize for performance later???
		switch(core->logic[i].type)
		{
		default:
			assert(0);   // TODO: unsupported type

		case WIRING_AND: name = "AND"; break;
		case WIRING_OR : name = "OR "; break;
		case WIRING_XOR: name = "XOR"; break;
		case WIRING_NOT: name = "NOT"; binary = 0; break;
		case WIRING_EQ : name = "EQ "; break;
		case WIRING_NEQ: name = "NEQ"; break;
		}

		fprintf(fp, "  logic %s size %d a %d",
		            name,
		            core->logic[i].size,
		            core->logic[i].a);

		if (binary)
			fprintf(fp, " b %d", core->logic[i].b);
		else
			fprintf(fp, "    ");

		fprintf(fp, " out %d", core->logic[i].out);

		print_debug(fp, core->logic[i].debug);
	}
	fprintf(fp, "\n");


	fprintf(fp, "connection count %d\n", core->numConnections);
	for (i=0; i<core->numConnections; i++)
	{
		fprintf(fp, "  connection ");

		if(core->conns[i].condition != WIRING_BIT_INVALID)
			fprintf(fp , "(condition %d) ", core->conns[i].condition);
		else
			fprintf(fp , "              ");

		// if(undirected)
		//	fprintf(fp , "(undirected) ");

		fprintf(fp, "size %d to %d from ",
		            core->conns[i].size,
		            core->conns[i].to);

		if (core->conns[i].from != WIRING_CONST_ZERO)
			fprintf(fp, "%d", core->conns[i].from);
		else
			fprintf(fp, "ZERO");

		print_debug(fp, core->conns[i].debug);
	}
	fprintf(fp, "\n");


	fprintf(fp, "assert count %d\n", core->numAsserts);
	for (i=0; i<core->numAsserts; i++)
	{
		fprintf(fp, "  assert %d", core->asserts[i].bit);
		print_debug(fp, core->asserts[i].debug);
	}
	fprintf(fp, "\n");


	return 0;
}


static void print_debug(FILE *fp, char *debug)
{
	if (debug == NULL)
	{
		fprintf(fp, "\n");
		return;
	}


	// TODO: eventually, add code that interprets (and can
	//       re-create) escape characters, especially \n
	fprintf(fp, "\tdebug=%s\n", debug);
}


