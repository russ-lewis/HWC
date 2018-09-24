COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage



all : hwcParser

hwcParser : lex.yy.c parser.tab.c
	$(COMP) -o hwcParser lex.yy.c parser.tab.c -lm


# https://stackoverflow.com/questions/13436832/bison-not-creating-the-tab-h-file
parser.tab.c parser.tab.h : parser.y pt/all.h
	bison --report=state -d parser.y

# I'm certain there's a way to do this without all the "pt/" before each filename
# but writing them out and writing this excuse comment was faster.

pt/all.h : pt/debug.h pt/expr.h pt/file.h pt/part.h pt/plugtype.h pt/stmt.h pt/type.h


lex.yy.c : lexer.src parser.tab.h
	flex lexer.src


##### CLEANING

clean : 
	-rm -f parser.tab.c
	-rm -f parser.tab.h
	-rm -f parser.output
	-rm -f lex.yy.c
#add @ in front of -rm is you wanna cancel the output to stdout
