from migen import *
from misoc.interconnect.csr import AutoCSR, CSRStatus

class DummyXADC(Module):
    def __init__(self):
        self.alarm = Signal(8)
        self.ot = Signal()
        self.do = Signal(16)
        self.drdy = Signal()
        self.daddr = Signal(7)
        self.den = Signal()
        self.dwe = Signal()
        self.di = Signal(16)
        self.dclk = Signal()
        self.reset = Signal()
        self.convst = Signal()
        self.convstclk = Signal()
        self.vp = Signal()
        self.vn = Signal()
        self.vauxp = Signal(16)
        self.vauxn = Signal(16)

        # Simulate XADC behavior
        self.sync += [
            If(self.den,
                self.do.eq(0x1234),  # Dummy data
                self.drdy.eq(1)
            ).Else(
                self.drdy.eq(0)
            )
        ]

class XADC(Module, AutoCSR):
    def __init__(self, xadc):
        self.alarm = Signal(8)
        self.ot = Signal()
        self.adc = [Signal((12, True)) for i in range(4)]

        self.temp = CSRStatus(12)
        self.v = CSRStatus(12)
        self.a = CSRStatus(12)
        self.b = CSRStatus(12)
        self.c = CSRStatus(12)
        self.d = CSRStatus(12)

        self.comb += [
            self.adc[0].eq(self.a.status),
            self.adc[1].eq(self.b.status),
            self.adc[2].eq(self.c.status),
            self.adc[3].eq(self.d.status),
        ]

        busy = Signal()
        channel = Signal(7)
        eoc = Signal()
        eos = Signal()
        data = Signal(16)
        drdy = Signal()

        vin = Cat(xadc.n[:2], Replicate(0, 6), xadc.n[2:4], Replicate(0, 6), xadc.n[4])
        vip = Cat(xadc.p[:2], Replicate(0, 6), xadc.p[2:4], Replicate(0, 6), xadc.p[4])

        dummy_xadc = DummyXADC()
        self.submodules += dummy_xadc

        self.comb += [
            dummy_xadc.daddr.eq(channel),
            dummy_xadc.den.eq(eoc),
            dummy_xadc.dwe.eq(0),
            dummy_xadc.di.eq(0),
            dummy_xadc.dclk.eq(ClockSignal()),
            dummy_xadc.reset.eq(ResetSignal()),
            dummy_xadc.convst.eq(0),
            dummy_xadc.convstclk.eq(0),
            dummy_xadc.vp.eq(vip[16]),
            dummy_xadc.vn.eq(vin[16]),
            dummy_xadc.vauxp.eq(vip[:16]),
            dummy_xadc.vauxn.eq(vin[:16]),
            self.alarm.eq(dummy_xadc.alarm),
            self.ot.eq(dummy_xadc.ot),
            data.eq(dummy_xadc.do),
            drdy.eq(dummy_xadc.drdy),
        ]

        channels = {
            0: self.temp,
            3: self.v,
            16: self.b,
            17: self.c,
            24: self.a,
            25: self.d,
        }

        self.sync += [
            If(drdy,
                Case(channel, dict((k, v.status.eq(data >> 4)) for k, v in channels.items())),
            )
        ]
