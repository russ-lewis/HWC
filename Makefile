COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage



ALL_HEADERS=$(wildcard pt/*.h semantic/*.h)

PARSE_SRC=lex.yy.c parser.tab.c
PT_SRC=pt/debug.c
SEM_SRC=semantic/names.c



all : hwcParser

hwcParser : $(ALL_HEADERS) $(PARSE_SRC) $(PT_SRC) $(SEM_SRC)
	$(COMP) -o hwcParser $(PARSE_SRC) $(PT_SRC) $(SEM_SRC) -lm


# https://stackoverflow.com/questions/13436832/bison-not-creating-the-tab-h-file
parser.tab.c parser.tab.h : parser.y pt/all.h
	bison --report=state -d parser.y


lex.yy.c : lexer.src parser.tab.h
	flex lexer.src


##### CLEANING

clean : 
	-rm -f parser.tab.c
	-rm -f parser.tab.h
	-rm -f parser.output
	-rm -f lex.yy.c
#add @ in front of -rm is you wanna cancel the output to stdout
