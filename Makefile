# --- RUSS WAS HERE ---

COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage

all : parser

##### Used by all files

parser : parser.tab.c
	$(COMP) -o parser parser.tab.c -lm

parser.tab.c : parser.y
	bison parser.y










#utility.o : utility.c
#	$(COMP) -c utility.c

##### CLEANING

clean : 
	-rm -f parser.tab.c parser
#add @ in front of -rm is you wanna cancel the output to stdout


# Test change to Makefile 
