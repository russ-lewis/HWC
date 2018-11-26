COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage

ROOT=..

WIRING=${ROOT}/wiring
SIM=sim



ALL_HEADERS=$(wildcard ${WIRING}/*.h ${SIM}/*.h)

PARSE_SRC=lex.yy.c parser.tab.c sim_main.c
WIRE_SRC=${WIRING}/write.c
SIM_SRC=${SIM}/graph.c



all : hwcSim

hwcSim : $(ALL_HEADERS) $(PARSE_SRC) $(WIRE_SRC) $(SIM_SRC)
	$(COMP) -I. -I${ROOT} -o hwcSim $(PARSE_SRC) $(WIRE_SRC) $(SIM_SRC) -lm


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
	-rm -f hwcSim
	-rm -f hwcSim.exe.stackdump
#add @ in front of -rm is you wanna cancel the output to stdout
