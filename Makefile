COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage



all : parser

##### Used by all files

parser : parser.tab.c lex.c
	$(COMP) -o parser parser.tab.c lex.c -lm -lfl

parser.tab.c : parser.y
	bison --verbose -d parser.y

lex.c: lex.src
	flex -olex.c lex.src



#utility.o : utility.c
#	$(COMP) -c utility.c

##### CLEANING

clean : 
	-rm -f parser.tab.c parser lex.c grammar.h
#add @ in front of -rm is you wanna cancel the output to stdout
