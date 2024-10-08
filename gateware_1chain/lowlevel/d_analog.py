from migen import *

class DummyODDR(Module):
    def __init__(self):
        self.D1 = Signal()
        self.D2 = Signal()
        self.C = Signal()
        self.CE = Signal()
        self.R = Signal()
        self.S = Signal()
        self.Q = Signal()

        self.comb += self.Q.eq(Mux(self.C, self.D2, self.D1))

class PitayaAnalog(Module):
    def __init__(self, adc, dac):
        self.comb += adc.cdcs.eq(1), adc.clk.eq(0b10)

        size = len(dac.data), True

        self.dummyadc = Signal.like(adc.data_b)

        self.adc_a = Signal(size)
        self.adc_b = Signal(size)
        self.dac_a = Signal(size)
        self.dac_b = Signal(size)

        adca = Signal.like(adc.data_b)
        adcb = Signal.like(adc.data_a)
        self.sync += adca.eq(adc.data_a), adcb.eq(adc.data_b)
        self.comb += [
            self.adc_a.eq(Cat(~adca[2:-1], adca[-1])),
            self.adc_b.eq(self.dummyadc),
        ]

        daca = Signal.like(dac.data)
        dacb = Signal.like(dac.data)
        self.sync += [
            daca.eq(Cat(~self.dac_a[:-1], self.dac_a[-1])),
            dacb.eq(Cat(~self.dac_b[:-1], self.dac_b[-1])),
        ]

        self.comb += dac.rst.eq(ResetSignal("sys"))

        clk_oddr = DummyODDR()
        wrt_oddr = DummyODDR()
        sel_oddr = DummyODDR()
        self.submodules += clk_oddr, wrt_oddr, sel_oddr

        self.comb += [
            clk_oddr.D1.eq(0), clk_oddr.D2.eq(1),
            clk_oddr.C.eq(ClockSignal("sys_double")),
            dac.clk.eq(clk_oddr.Q),
            clk_oddr.CE.eq(1), clk_oddr.R.eq(0), clk_oddr.S.eq(0),

            wrt_oddr.D1.eq(0), wrt_oddr.D2.eq(1),
            wrt_oddr.C.eq(ClockSignal("sys_double")),
            dac.wrt.eq(wrt_oddr.Q),
            wrt_oddr.CE.eq(1), wrt_oddr.R.eq(0), wrt_oddr.S.eq(0),

            sel_oddr.D1.eq(0), sel_oddr.D2.eq(1),
            sel_oddr.C.eq(ClockSignal("sys")),
            dac.sel.eq(sel_oddr.Q),
            sel_oddr.CE.eq(1), sel_oddr.R.eq(0), sel_oddr.S.eq(0),
        ]

        for i in range(len(dac.data)):
            data_oddr = DummyODDR()
            self.submodules += data_oddr
            self.comb += [
                data_oddr.D1.eq(daca[i]),
                data_oddr.D2.eq(dacb[i]),
                data_oddr.C.eq(ClockSignal("sys")),
                dac.data[i].eq(data_oddr.Q),
                data_oddr.CE.eq(1), data_oddr.R.eq(0), data_oddr.S.eq(0),
            ]
