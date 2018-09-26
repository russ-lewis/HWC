COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage



ALL_PT=$(wildcard pt/*.h)


all : hwcParser

hwcParser : lex.yy.c parser.tab.c $(ALL_PT)
	$(COMP) -o hwcParser lex.yy.c parser.tab.c pt/debug.c -lm


# https://stackoverflow.com/questions/13436832/bison-not-creating-the-tab-h-file
parser.tab.c parser.tab.h : parser.y pt/debug.c
	bison --report=state -d parser.y


lex.yy.c : lexer.src parser.tab.h
	flex lexer.src


##### CLEANING

clean : 
	-rm -f parser.tab.c
	-rm -f parser.tab.h
	-rm -f parser.output
	-rm -f lex.yy.c
	-rm -f hwcParser
#add @ in front of -rm is you wanna cancel the output to stdout
