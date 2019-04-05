-- Taken from http://vhdlguru.blogspot.com/2011/07/delay-in-vhdl-without-using-wait-for.html
--
-- Russ says: I have no idea if this is good VHDL code or not.  But it's *an*
--            example.  I have provided the equivalent HWC code in another
--            file.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;

entity delay is
port(   Clk : in std_logic;
        valid_data : in std_logic; -- goes high when the input is valid.
        data_in : in std_logic; -- the data input
        data_out : out std_logic --the delayed input data.
        );
end delay;

architecture Behaviora of delay is

signal c : integer := 0;
constant d : integer := 100; --number of clock cycles by which input should be delayed.
signal data_temp : std_logic := '0';
type state_type is (idle,delay_c); --defintion of state machine type
signal next_s : state_type; --declare the state machine signal.

begin

process(Clk)
begin
    if(rising_edge(Clk)) then
        case next_s is
            when idle =>
                if(valid_data= '1') then
                    next_s <= delay_c;
                    data_temp <= data_in; --register the input data.
                    c <= 1;
                end if;
            when delay_c =>
                if(c = d) then
                    c <= 1; --reset the count
                    data_out <= data_temp; --assign the output
                    next_s <= idle; --go back to idle state and wait for another valid data.
                else
                    c <= c + 1;
                end if;
            when others =>
                NULL;
        end case;
    end if;
end process;   

   
end Behaviora;

