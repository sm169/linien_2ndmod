# This file is part of Linien and based on redpid.
#
# Copyright (C) 2016-2024 Linien Authors (https://github.com/linien-org/linien#license)
#
# Linien is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linien is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linien.  If not, see <http://www.gnu.org/licenses/>.

from migen import Cat, Module, Signal, TSTriple
from migen.genlib.cdc import MultiReg
from misoc.interconnect.csr import AutoCSR, CSRStatus, CSRStorage

class Gpio(Module, AutoCSR):
    def __init__(self, pins):
        # Number of GPIO pins
        n = len(pins)

        # Input signal for all pins
        self.i = Signal(n)
        # Output signal for all pins
        self.o = Signal(n)

        # CSR register for reading input states
        self.ins = CSRStatus(n)
        # CSR register for setting output states
        self.outs = CSRStorage(n)
        # CSR register for setting output enables
        self.oes = CSRStorage(n)

        ###

        # Create tristate buffers for each pin
        t = [TSTriple(1) for i in range(n)]
        # Connect tristate buffers to physical pins
        self.specials += [ti.get_tristate(pins[i]) for i, ti in enumerate(t)]
        # Use MultiReg for input synchronization
        self.specials += MultiReg(Cat([ti.i for ti in t]), self.i)

        # Combinatorial logic for connecting signals
        self.comb += [
            # Set output values from CSR or internal signal
            Cat([ti.o for ti in t]).eq(self.outs.storage | self.o),
            # Set output enables from CSR
            Cat([ti.oe for ti in t]).eq(self.oes.storage),
            # Update input CSR with current input values
            self.ins.status.eq(self.i),
        ]
