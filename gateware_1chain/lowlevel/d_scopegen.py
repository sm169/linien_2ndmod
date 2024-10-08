from migen import *
from misoc.interconnect.csr import AutoCSR, CSRStorage

from .pitaya_ps import sys_layout

class DummyRedPitayaScope(Module):
    def __init__(self):
        self.automatically_rearm_i = Signal()
        self.adc_a_i = Signal(14)
        self.adc_b_i = Signal(14)
        self.adc_a_q_i = Signal(14)
        self.adc_b_q_i = Signal(14)
        self.adc_clk_i = Signal()
        self.adc_rstn_i = Signal()
        self.trig_ext_i = Signal()
        self.trig_asg_i = Signal()
        self.sys_clk_i = Signal()
        self.sys_rstn_i = Signal()
        self.sys_addr_i = Signal(32)
        self.sys_wdata_i = Signal(32)
        self.sys_sel_i = Signal(4)
        self.sys_wen_i = Signal()
        self.sys_ren_i = Signal()
        self.sys_rdata_o = Signal(32)
        self.sys_err_o = Signal()
        self.sys_ack_o = Signal()
        self.written_data = Signal(14)
        self.scope_position = Signal(14)
        self.scope_writing_now = Signal()

        # Simple simulation logic
        self.sync += [
            If(self.sys_wen_i,
                self.sys_rdata_o.eq(self.sys_wdata_i),
                self.sys_ack_o.eq(1)
            ).Elif(self.sys_ren_i,
                self.sys_rdata_o.eq(self.adc_a_i),
                self.sys_ack_o.eq(1)
            ).Else(
                self.sys_ack_o.eq(0)
            ),
            self.written_data.eq(self.adc_a_i),
            self.scope_position.eq(self.scope_position + 1),
            self.scope_writing_now.eq(self.sys_wen_i | self.sys_ren_i)
        ]

class ScopeGen(Module, AutoCSR):
    def __init__(self, width=25):
        self.gpio_trigger = Signal()
        self.sweep_trigger = Signal()
        self.automatically_rearm = Signal()
        self.automatically_trigger = Signal()
        self.external_trigger = CSRStorage(1)
        self.scope_sys = Record(sys_layout)
        self.asg_sys = Record(sys_layout)

        adc_a = Signal((width, True))
        adc_a_q = Signal((width, True))
        adc_b = Signal((width, True))
        adc_b_q = Signal((width, True))
        dac_a = Signal((width, True))
        dac_b = Signal((width, True))

        self.signal_in = adc_a, adc_b, adc_a_q, adc_b_q
        self.signal_out = dac_a, dac_b
        self.state_in = ()
        self.state_out = ()

        asg_a = Signal((14, True))
        asg_b = Signal((14, True))
        asg_trig = Signal()

        s = width - len(asg_a)
        self.comb += dac_a.eq(asg_a << s), dac_b.eq(asg_b << s)

        self.writing_data_now = Signal()
        self.scope_written_data = Signal((14, True))
        self.scope_position = Signal(14)

        scope = DummyRedPitayaScope()
        self.submodules += scope

        self.comb += [
            scope.automatically_rearm_i.eq(self.automatically_rearm),
            scope.adc_a_i.eq(adc_a >> s),
            scope.adc_b_i.eq(adc_b >> s),
            scope.adc_a_q_i.eq(adc_a_q >> s),
            scope.adc_b_q_i.eq(adc_b_q >> s),
            scope.adc_clk_i.eq(ClockSignal()),
            scope.adc_rstn_i.eq(~ResetSignal()),
            scope.trig_ext_i.eq(self.gpio_trigger | self.sweep_trigger),
            scope.trig_asg_i.eq(asg_trig),
            scope.sys_clk_i.eq(self.scope_sys.clk),
            scope.sys_rstn_i.eq(self.scope_sys.rstn),
            scope.sys_addr_i.eq(self.scope_sys.addr),
            scope.sys_wdata_i.eq(self.scope_sys.wdata),
            scope.sys_sel_i.eq(self.scope_sys.sel),
            scope.sys_wen_i.eq(self.scope_sys.wen),
            scope.sys_ren_i.eq(self.scope_sys.ren),
            self.scope_sys.rdata.eq(scope.sys_rdata_o),
            self.scope_sys.err.eq(scope.sys_err_o),
            self.scope_sys.ack.eq(scope.sys_ack_o),
            self.scope_written_data.eq(scope.written_data),
            self.scope_position.eq(scope.scope_position),
            self.writing_data_now.eq(scope.scope_writing_now),
        ]
