COMP=gcc -Wall -g -std=gnu99
#-fprofile-arcs -ftest-coverage

ROOT=..

WIRING=${ROOT}/wiring
SIM=sim



ALL_HEADERS=$(wildcard ${WIRING}/*.h ${SIM}/*.h)

PARSE_SRC=sim_main.c
WIRE_SRC=${WIRING}/write.c ${WIRING}/lex.yy.c ${WIRING}/parser.tab.c
SIM_SRC=${SIM}/state.c



all : hwcSim

hwcSim : $(ALL_HEADERS) $(PARSE_SRC) $(WIRE_SRC) $(SIM_SRC)
	$(COMP) -I. -I${ROOT} -o hwcSim $(PARSE_SRC) $(WIRE_SRC) $(SIM_SRC) -lm


${WIRING}/parser.tab.c ${WIRING}/parser.tab.h ${WIRING}/lex.yy.c : ${WIRING}/parser.y ${WIRING}/lexer.src 
	make -C ${WIRING} parser.tab.c parser.tab.h lex.yy.c



##### CLEANING

clean : 
	make -C ${WIRING} clean
	-rm -f hwcSim
	-rm -f hwcSim.exe.stackdump
#add @ in front of -rm is you wanna cancel the output to stdout
