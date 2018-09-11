COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage

all : hwcParser

hwcParser : lex.yy.c parser.tab.c
	$(COMP) -o hwcParser lex.yy.c parser.tab.c -lm


parser.tab.c : parser.y
	bison parser.y


# https://stackoverflow.com/questions/13436832/bison-not-creating-the-tab-h-file
parser.tab.h : parser.y
	bison -d parser.y


lex.yy.c : lexer.src parser.tab.h
	flex lexer.src


##### CLEANING

clean : 
	-rm -f parser.tab.c
	-rm -f parser.tab.h
	-rm -f lex.yy.c
	-rm -f hwcParser
#add @ in front of -rm is you wanna cancel the output to stdout
