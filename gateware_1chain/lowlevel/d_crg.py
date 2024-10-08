from migen import *

class DummyIBUFGDS(Module):
    def __init__(self):
        self.I = Signal()
        self.IB = Signal()
        self.O = Signal()
        self.comb += self.O.eq(self.I ^ self.IB)

class DummyBUFG(Module):
    def __init__(self):
        self.I = Signal()
        self.O = Signal()
        self.comb += self.O.eq(self.I)

class DummyPLLE2_BASE(Module):
    def __init__(self):
        self.CLKIN1 = Signal()
        self.CLKFBIN = Signal()
        self.CLKFBOUT = Signal()
        self.CLKOUT0 = Signal()
        self.CLKOUT1 = Signal()
        self.CLKOUT2 = Signal()
        self.CLKOUT3 = Signal()
        self.CLKOUT4 = Signal()
        self.CLKOUT5 = Signal()
        self.LOCKED = Signal(reset=1)
        self.comb += [
            self.CLKFBOUT.eq(self.CLKFBIN),
            self.CLKOUT0.eq(self.CLKIN1),
            self.CLKOUT1.eq(self.CLKIN1),
            self.CLKOUT2.eq(self.CLKIN1),
            self.CLKOUT3.eq(self.CLKIN1),
            self.CLKOUT4.eq(self.CLKIN1),
            self.CLKOUT5.eq(self.CLKIN1),
        ]

class DummyFD(Module):
    def __init__(self):
        self.C = Signal()
        self.D = Signal()
        self.Q = Signal()
        self.sync += self.Q.eq(self.D)

class CRG(Module):
    def __init__(self, clk_adc, clk_ps, rst):
        self.clock_domains.cd_sys_quad = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys_double = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys_slow = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys_ps = ClockDomain()
        self.comb += [self.cd_sys_ps.clk.eq(clk_ps), self.cd_sys_ps.rst.eq(rst)]

        clk_adci = Signal()
        clk_adcb = Signal()
        clk = Signal(6)
        clkb = Signal(6)
        clk_fb = Signal()
        clk_fbb = Signal()
        locked = Signal()

        ibufgds = DummyIBUFGDS()
        bufg1 = DummyBUFG()
        pll = DummyPLLE2_BASE()
        bufg2 = DummyBUFG()
        fd = DummyFD()

        self.submodules += ibufgds, bufg1, pll, bufg2, fd

        self.comb += [
            ibufgds.I.eq(clk_adc.p),
            ibufgds.IB.eq(clk_adc.n),
            clk_adci.eq(ibufgds.O),
            bufg1.I.eq(clk_adci),
            clk_adcb.eq(bufg1.O),
            pll.CLKIN1.eq(clk_adcb),
            pll.CLKFBIN.eq(clk_fbb),
            clk_fb.eq(pll.CLKFBOUT),
            clk[0].eq(pll.CLKOUT0),
            clk[1].eq(pll.CLKOUT1),
            clk[2].eq(pll.CLKOUT2),
            clk[3].eq(pll.CLKOUT3),
            clk[4].eq(pll.CLKOUT4),
            clk[5].eq(pll.CLKOUT5),
            locked.eq(pll.LOCKED),
            bufg2.I.eq(clk_fb),
            clk_fbb.eq(bufg2.O),
        ]

        for i, d in enumerate([self.cd_sys_quad, self.cd_sys_double, self.cd_sys, self.cd_sys_slow]):
            bufg = DummyBUFG()
            self.submodules += bufg
            self.comb += [
                bufg.I.eq(clk[i]),
                d.clk.eq(bufg.O),
            ]

        self.comb += [
            fd.D.eq(~locked),
            fd.C.eq(self.cd_sys.clk),
            self.cd_sys.rst.eq(fd.Q),
        ]
