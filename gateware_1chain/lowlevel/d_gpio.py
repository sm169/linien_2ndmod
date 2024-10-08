from migen import *
from migen.genlib.cdc import MultiReg
from misoc.interconnect.csr import AutoCSR, CSRStatus, CSRStorage

class SimGpio(Module, AutoCSR):
    def __init__(self, pins):
        n = len(pins)
        self.i = Signal(n)
        self.o = Signal(n)
        self.ins = CSRStatus(n)
        self.outs = CSRStorage(n)
        self.oes = CSRStorage(n)

        ###

        # Simulate tristate behavior
        for i in range(n):
            pin = Signal()
            self.comb += [
                If(self.oes.storage[i],
                    pin.eq(self.outs.storage[i] | self.o[i])
                ).Else(
                    pin.eq(0)
                )
            ]
            self.sync += self.i[i].eq(pin)

        self.specials += MultiReg(self.i, self.ins.status)

    def get_tristate(self, pin):
        return pin

#This SimGpio class simulates the behavior of the original Gpio module, including the tristate functionality, in a way that's compatible with Migen's simulator. It uses a combination of combinatorial and synchronous logic to emulate the tristate behavior of each pin.
