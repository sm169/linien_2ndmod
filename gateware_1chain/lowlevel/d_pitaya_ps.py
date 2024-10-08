from migen import *
from misoc.interconnect import csr_bus, wishbone

class DummyProcessingSystem7(Module):
    def __init__(self):
        self.fclk = [Signal() for _ in range(4)]
        self.frstn = [Signal() for _ in range(4)]
        self.axi = Record(axi_layout)

        # Simulate clock and reset
        for i in range(4):
            self.comb += self.fclk[i].eq(ClockSignal())
            self.comb += self.frstn[i].eq(~ResetSignal())

class DummyAxiSlave(Module):
    def __init__(self):
        self.axi = Record(axi_layout)
        self.sys = Record(sys_layout)

        # Simple pass-through logic
        self.comb += [
            self.sys.clk.eq(self.axi.aclk),
            self.sys.rstn.eq(self.axi.arstn),
            self.sys.addr.eq(self.axi.araddr),
            self.sys.wdata.eq(self.axi.wdata),
            self.sys.sel.eq(self.axi.wstrb),
            self.sys.wen.eq(self.axi.awvalid & self.axi.wvalid),
            self.sys.ren.eq(self.axi.arvalid),
            self.axi.rdata.eq(self.sys.rdata),
            self.axi.bresp.eq(0),
            self.axi.rresp.eq(0),
            self.axi.bvalid.eq(self.sys.ack),
            self.axi.rvalid.eq(self.sys.ack),
        ]

class PitayaPS(Module):
    def __init__(self, cpu):
        self.fclk = Signal(4)
        self.frstn = Signal(4)

        self.submodules.axi = Axi2Sys()
        axi = self.axi.axi

        ps7 = DummyProcessingSystem7()
        self.submodules += ps7

        self.comb += [
            axi.aclk.eq(ps7.fclk[0]),
            axi.arstn.eq(ps7.frstn[0]),
            self.fclk.eq(Cat(ps7.fclk)),
            self.frstn.eq(Cat(ps7.frstn)),
        ]

        # Connect AXI signals
        for name, size in axi_layout:
            self.comb += getattr(axi, name).eq(getattr(ps7.axi, name))

class Axi2Sys(Module):
    def __init__(self):
        self.sys = Record(sys_layout)
        self.axi = Record(axi_layout)

        axi_slave = DummyAxiSlave()
        self.submodules += axi_slave

        self.comb += [
            self.axi.connect(axi_slave.axi),
            self.sys.connect(axi_slave.sys)
        ]

sys_layout = [
    ("rstn", 1, DIR_M_TO_S),
    ("clk", 1, DIR_M_TO_S),
    ("addr", 32, DIR_M_TO_S),
    ("wdata", 32, DIR_M_TO_S),
    ("sel", 4, DIR_M_TO_S),
    ("wen", 1, DIR_M_TO_S),
    ("ren", 1, DIR_M_TO_S),
    ("rdata", 32, DIR_S_TO_M),
    ("err", 1, DIR_S_TO_M),
    ("ack", 1, DIR_S_TO_M),
]


axi_layout = [
    ("arvalid", 1),
    ("awvalid", 1),
    ("bready", 1),
    ("rready", 1),
    ("wlast", 1),
    ("wvalid", 1),
    ("arid", 12),
    ("awid", 12),
    ("wid", 12),
    ("arburst", 2),
    ("arlock", 2),
    ("arsize", 3),
    ("awburst", 2),
    ("awlock", 2),
    ("awsize", 3),
    ("arprot", 3),
    ("awprot", 3),
    ("araddr", 32),
    ("awaddr", 32),
    ("wdata", 32),
    ("arcache", 4),
    ("arlen", 4),
    ("arqos", 4),
    ("awcache", 4),
    ("awlen", 4),
    ("awqos", 4),
    ("wstrb", 4),
    ("aclk", 1),
    ("arready", 1),
    ("awready", 1),
    ("bvalid", 1),
    ("rlast", 1),
    ("rvalid", 1),
    ("wready", 1),
    ("bid", 12),
    ("rid", 12),
    ("bresp", 2),
    ("rresp", 2),
    ("rdata", 32),
    ("arstn", 1),
]

class Sys2CSR(Module):
    def __init__(self):
        self.csr = csr_bus.Interface()
        self.sys = Record(sys_layout)

        ###

        stb = Signal()
        self.sync += [
            stb.eq(self.sys.wen | self.sys.ren),
            self.csr.adr.eq(self.sys.addr[2:]),
            self.csr.we.eq(self.sys.wen),
            self.csr.dat_w.eq(self.sys.wdata),
            self.sys.ack.eq(stb),
            self.sys.rdata.eq(self.csr.dat_r),
        ]

class SysInterconnect(Module):
    def __init__(self, master, *slaves):
        cs = Signal(max=len(slaves))
        self.comb += cs.eq(master.addr[20:23])
        rets = []
        for i, s in enumerate(slaves):
            sel = Signal()
            self.comb += [
                sel.eq(cs == i),
                s.clk.eq(master.clk),
                s.rstn.eq(master.rstn),
                s.addr.eq(master.addr),
                s.wdata.eq(master.wdata),
                s.sel.eq(master.sel),
                s.wen.eq(sel & master.wen),
                s.ren.eq(sel & master.ren),
            ]
            ret = Cat(s.err, s.ack, s.rdata)
            rets.append(Replicate(sel, len(ret)) & ret)
        self.comb += Cat(master.err, master.ack, master.rdata).eq(reduce(or_, rets))

class SysCDC(Module):
    def __init__(self, cd_target="sys"):
        self.source = Record(sys_layout)
        self.target = Record(sys_layout)

        # Simple pass-through logic for simulation
        self.comb += [
            self.target.clk.eq(ClockSignal(cd_target)),
            self.target.rstn.eq(~ResetSignal(cd_target)),
            self.target.addr.eq(self.source.addr),
            self.target.wdata.eq(self.source.wdata),
            self.target.sel.eq(self.source.sel),
            self.target.wen.eq(self.source.wen),
            self.target.ren.eq(self.source.ren),
            self.source.rdata.eq(self.target.rdata),
            self.source.err.eq(self.target.err),
            self.source.ack.eq(self.target.ack)
        ]