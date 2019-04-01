# HWC
Code repository for Hardware C

~~~
part Mux
{
   public Data[4] in;
   public bit[2]  control;
   public Data    out;
   
   for (i; 0..4)
       if (control == i)
           out = in[i];
}
~~~

## Key directories:
- spec/
  Design spec, describes how the language works
- hwcCompile/
  Contains the source for the compiler
- hwcSim/
  Simulator, planned to eventually use ncurses to display colored/manipulated source code as a quasi-GUI
- hwcSim_raw/
  Simulator with non-ncurses output.  Not suitable for human consumption, except for experts; used for running unit tests.  (This shares all code, except for the output code, with hwcSim/
- wiring/, graph/, sim/
  Directories containing code that is shared across two or more tools
