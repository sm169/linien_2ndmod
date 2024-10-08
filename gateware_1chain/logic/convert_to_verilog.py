# logic/convert_to_verilog.py

from .generate_sine_wave import generate_sine_wave
from migen import *
from migen.fhdl.verilog import convert
from ..hw_platform import Platform
from ..linien_module import RootModule

platform = Platform()
dut = RootModule(platform)

convert(dut, name="top").write("C:\\linien_2ndmod\\gateware_1chain\\cocotb\\generated_full_design.v")

#generate_sine_wave()