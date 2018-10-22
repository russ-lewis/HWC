COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage

ROOT=..

WIRING=${ROOT}/wiring
SIM=${ROOT}/sim



ALL_HEADERS=$(wildcard ${WIRING}/*.h ${SIM}/*.h)

PARSE_SRC=lex.yy.c parser.tab.c compile.c
WIRE_SRC=${WIRING}/build_part.c ${WIRING}/write.c



all : hwcCompile

hwcCompile : $(ALL_HEADERS) $(PARSE_SRC) $(WIRE_SRC)
	$(COMP) -I. -I${ROOT} -o hwcCompile $(PARSE_SRC) $(WIRE_SRC) -lm


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
#add @ in front of -rm is you wanna cancel the output to stdout
