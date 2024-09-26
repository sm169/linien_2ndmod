from gateware.logic.modulate2 import Modulate
from migen import *
from migen.fhdl.verilog import convert

dut = Modulate(wid=14)

convert(dut, name="mod").write("mod.v")