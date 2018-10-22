COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage



ALL_HEADERS=$(wildcard pt/*.h semantic/*.h)

PARSE_SRC=lex.yy.c parser.tab.c compile.c
PT_SRC=pt/debug.c
SEM_SRC=semantic/names.c semantic/debug.c \
        semantic/phase1_file.c semantic/phase1_part.c semantic/phase1_plugtype.c \
        semantic/phase2_part.c \
        semantic/phase3_part.c \
        semantic/phase4_part.c semantic/phase4_plugtype.c
WIRE_SRC=wiring/build_part.c



all : hwcCompile

hwcCompile : $(ALL_HEADERS) $(PARSE_SRC) $(PT_SRC) $(SEM_SRC) $(WIRE_SRC)
	$(COMP) -I. -o hwcCompile $(PARSE_SRC) $(PT_SRC) $(SEM_SRC) $(WIRE_SRC) -lm


# https://stackoverflow.com/questions/13436832/bison-not-creating-the-tab-h-file
parser.tab.c parser.tab.h : parser.y
	bison --report=state -d parser.y


lex.yy.c : lexer.src parser.tab.h
	flex lexer.src


##### CLEANING

clean : 
	-rm -f parser.tab.c
	-rm -f parser.tab.h
	-rm -f parser.output
	-rm -f lex.yy.c
	-rm -f hwcCompile
#add @ in front of -rm if you wanna cancel the output to stdout
