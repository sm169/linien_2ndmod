from migen import *
from misoc.interconnect.csr import AutoCSR, CSRStatus

class DummyDNA_PORT(Module):
    def __init__(self):
        self.DIN = Signal()
        self.READ = Signal()
        self.SHIFT = Signal()
        self.CLK = Signal()
        self.DOUT = Signal()

        # Simulate DNA readout
        dna = Signal(57, reset=0x123456789ABCDEF)  # Example DNA value
        counter = Signal(max=57)

        self.sync += [
            If(self.READ & self.SHIFT,
                counter.eq(0)
            ).Elif(self.SHIFT,
                If(counter < 57,
                    counter.eq(counter + 1)
                )
            )
        ]

        self.comb += self.DOUT.eq((dna >> counter) & 1)

class DNA(Module, AutoCSR):
    def __init__(self, version=0b1000001):
        n = 64
        self.dna = CSRStatus(n, reset=version << 57)

        do = Signal()
        cnt = Signal(max=2 * n + 1)

        dna_port = DummyDNA_PORT()
        self.submodules += dna_port

        self.comb += [
            dna_port.DIN.eq(self.dna.status[-1]),
            dna_port.READ.eq(cnt < 2),
            dna_port.SHIFT.eq(1),
            dna_port.CLK.eq(cnt[0]),
            do.eq(dna_port.DOUT)
        ]

        self.sync += [
            If(cnt < 2 * n,
                cnt.eq(cnt + 1),
                If(cnt[0], self.dna.status.eq(Cat(do, self.dna.status)))
            )
        ]
