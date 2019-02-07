COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage

ROOT=..

WIRING=${ROOT}/wiring
GRAPH=${ROOT}/graph
SIM=sim



ALL_HEADERS=$(wildcard ${WIRING}/*.h ${SIM}/*.h)

MAIN_SRC=sim_main.c
WIRE_SRC=${WIRING}/write.c ${WIRING}/lex.yy.c ${WIRING}/parser.tab.c
GRAPH_SRC=${GRAPH}/core.c ${GRAPH}/overlapTable.c
SIM_SRC=${SIM}/state.c ${SIM}/tick.c ${SIM}/notify.c ${SIM}/runtime_errors.c



all : hwcSim

hwcSim : $(ALL_HEADERS) $(MAIN_SRC) $(WIRE_SRC) $(GRAPH_SRC) $(SIM_SRC)
	$(COMP) -I. -I${ROOT} -o hwcSim $(MAIN_SRC) $(WIRE_SRC) $(GRAPH_SRC) $(SIM_SRC) -lm


${WIRING}/parser.tab.c ${WIRING}/parser.tab.h ${WIRING}/lex.yy.c : ${WIRING}/parser.y ${WIRING}/lexer.src 
	make -C ${WIRING} parser.tab.c parser.tab.h lex.yy.c



##### CLEANING

clean : 
	make -C ${WIRING} clean
	-rm -f hwcSim
	-rm -f hwcSim.exe.stackdump
#add @ in front of -rm is you wanna cancel the output to stdout
