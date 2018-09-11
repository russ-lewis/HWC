COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage

all : hwcParser

hwcParser : lex.yy.c parser.tab.c
	$(COMP) -o hwcParser lex.yy.c parser.tab.c -lm


parser.tab.c : parser.y
	bison parser.y


lex.yy.c : lexer.src
	flex lexer.src



##### CLEANING

clean : 
	-rm -f parser.tab.c
	-rm -f lex.yy.c
	-rm -f hwcParser
#add @ in front of -rm is you wanna cancel the output to stdout
