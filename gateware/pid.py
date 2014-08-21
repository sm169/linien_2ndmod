# Robert Jordens <jordens@gmail.com> 2014

from migen.fhdl.std import *
from migen.genlib.record import *
from migen.bank.description import *

from .filter import Filter
from .iir import Iir
from .limit import LimitCSR
from .sweep import SweepCSR
from .relock import Relock
from .modulate import Modulate, Demodulate


signal_width = 25
coeff_width = 18


class InChain(Filter):
    def __init__(self, width=14):
        Filter.__init__(self, width=signal_width)
        self.adc = Signal((width, True))
        self.submodules.limit = LimitCSR(width=signal_width)
        self.submodules.iir_a = Iir(width=signal_width,
                coeff_width=coeff_width, order=1)
        self.submodules.demod = Demodulate(width=signal_width)

        self.r_tap = CSRStorage(2, reset=0)
        self.r_adc = CSRStatus(width)

        ###

        ys = Array([self.x, self.limit.y, self.iir_a.y, self.demod.y])
        self.comb += [
                self.x.eq(self.adc << (signal_width - width)),
                self.limit.x.eq(self.x),
                self.iir_a.x.eq(self.limit.y),
        ]
        self.sync += [
                self.r_adc.status.eq(self.adc),
                self.demod.x.eq(self.iir_a.y),
                self.y.eq(ys[self.r_tap.storage])
        ]


class OutChain(Filter):
    def __init__(self, width=14):
        Filter.__init__(self, width=signal_width)

        self.submodules.iir_a = Iir(width=signal_width,
                coeff_width=coeff_width, order=1)
        self.submodules.iir_b = Iir(width=signal_width,
                coeff_width=coeff_width, order=1)
        self.submodules.iir_c = Iir(width=signal_width,
                coeff_width=coeff_width, order=2)
        self.submodules.iir_d = Iir(width=signal_width,
                coeff_width=coeff_width, order=2)

        self.submodules.relock = Relock(width=signal_width)
        self.submodules.sweep = SweepCSR(width=signal_width)
        self.submodules.mod = Modulate(width=signal_width)

        y = self.y, self.relock.y, self.sweep.y, self.mod.y
        guard = log2_int(len(y), need_pow2=False)
        self.submodules.limit = LimitCSR(width=signal_width + guard)
        self.dac = Signal((width, True))

        self.r_tap = CSRStorage(3, reset=0)
        self.r_dac = CSRStatus(width)

        ys = Array([self.x, self.iir_a.y, self.iir_b.y,
            self.iir_c.y, self.iir_d.y])
        self.comb += [
                self.limit.x.eq(optree("+", y)),
                self.dac.eq(self.limit.y[signal_width - width:]),
        ]
        self.sync += [
                self.r_dac.status.eq(self.dac),
                self.iir_a.x.eq(self.x),
                self.iir_b.x.eq(self.iir_a.y),
                self.iir_c.x.eq(self.iir_b.x),
                self.iir_d.x.eq(self.iir_c.x),
                self.y.eq(ys[self.r_tap.storage]),
        ]


class IOMux(Module, AutoCSR):
    def __init__(self, ins, outs):
        r = Array([i.y for i in ins] + [o.y for o in outs])
        for i, o in zip("abcdef", outs):
            m = CSRStorage(len(ins), reset=0, name="mux_%s" % i)
            setattr(self, "r_mux_%s" % i, m)
            self.comb += o.x.eq(optree("+", [Mux(m.storage[j], ini.y, 0)
                for j, ini in enumerate(ins)]))
            m = CSRStorage(log2_int(len(r), need_pow2=False),
                    reset=0, name="mux_relock_%s" % i)
            setattr(self, "r_mux_relock_%s" %i, m)
            self.sync += o.relock.x.eq(r[m.storage])


class Pid(Module, AutoCSR):
    def __init__(self):
        self.r_version = CSRStatus(8)
        self.r_version.status.reset = 1

        self.submodules.in_a = InChain(14)
        self.submodules.in_b = InChain(14)
        self.submodules.out_a = OutChain(14)
        self.submodules.out_b = OutChain(14)
        self.submodules.iomux = IOMux([self.in_a, self.in_b],
                [self.out_a, self.out_b])
