COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage

ROOT=..

PT=pt
SEMANTIC=semantic
WIRING=${ROOT}/wiring
SIM=${ROOT}/sim



ALL_HEADERS=$(wildcard ${PT}/*.h ${SEMANTIC}/*.h ${WIRING}/*.h ${SIM}/*.h)

PARSE_SRC=lex.yy.c parser.tab.c compile_main.c
PT_SRC=${PT}/debug.c
SEM_SRC=${SEMANTIC}/names.c ${SEMANTIC}/debug.c \
        ${SEMANTIC}/phase10_file.c ${SEMANTIC}/phase10_part.c ${SEMANTIC}/phase10_plugtype.c \
        ${SEMANTIC}/phase20_part.c \
        ${SEMANTIC}/phase30_part.c \
        ${SEMANTIC}/phase40_part.c ${SEMANTIC}/phase40_plugtype.c \
        ${SEMANTIC}/stmt.c ${SEMANTIC}/expr.c ${SEMANTIC}/decl.c
WIRE_SRC=${WIRING}/build_part.c ${WIRING}/write.c



all : hwcCompile

hwcCompile : $(ALL_HEADERS) $(PARSE_SRC) $(PT_SRC) $(SEM_SRC) $(WIRE_SRC)
	$(COMP) -I. -I${ROOT} -o hwcCompile $(PARSE_SRC) $(PT_SRC) $(SEM_SRC) $(WIRE_SRC) -lm


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
	-rm -f hwcCompile.exe.stackdump
#add @ in front of -rm is you wanna cancel the output to stdout
