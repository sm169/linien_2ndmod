from migen import *
from ..linien_module import LinienModule
from ..hw_platform import Platform
from ..lowlevel.analog import PitayaAnalog
from ..lowlevel.crg import CRG
from ..lowlevel.dna import DNA
from ..lowlevel.gpio import Gpio
from ..lowlevel.pitaya_ps import PitayaPS
from ..lowlevel.xadc import XADC
from ..lowlevel.scopegen import ScopeGen


def input_signal():
    # Produces a signal that can be interated through in testbench to simulate input to the linien module
    pass

def create_sim_pitaya_analog():
    class SimPitayaAnalog(PitayaAnalog):
        def __init__(self, adc, dac):
            super().__init__(adc, dac)
            self.specials
            self.sync.sys_double += [
                self.dac.clk.eq(~self.dac.clk),
                self.dac.wrt.eq(~self.dac.wrt),
            ]
            self.sync.sys += self.dac.sel.eq(~self.dac.sel)
    return SimPitayaAnalog

def create_sim_crg():
    class SimCRG(CRG):
        def __init__(self, clk_adc, clk_ps, rst):
            super().__init__(clk_adc, clk_ps, rst)
            self.specials = []
            self.clock_domains.cd_sys_quad = ClockDomain()
            self.clock_domains.cd_sys_double = ClockDomain()
            self.clock_domains.cd_sys = ClockDomain()
            self.clock_domains.cd_sys_slow = ClockDomain()
            self.sync += [
                self.cd_sys_quad.clk.eq(~self.cd_sys_quad.clk),
                self.cd_sys_double.clk.eq(~self.cd_sys_double.clk),
                self.cd_sys.clk.eq(~self.cd_sys.clk),
                self.cd_sys_slow.clk.eq(~self.cd_sys_slow.clk),
            ]
    return SimCRG

def create_sim_dna():
    class SimDNA(DNA):
        def __init__(self, version=0b1000001):
            super().__init__(version)
            self.specials = []
            self.sync += [
                If(self.cnt < 2 * self.n,
                    self.cnt.eq(self.cnt + 1),
                    If(self.cnt[0], self.dna.status.eq(Cat(self.do, self.dna.status)))
                )
            ]
    return SimDNA

def create_sim_gpio():
    class SimGpio(Gpio):
        def __init__(self, pins):
            super().__init__(pins)
            self.specials = []
            self.sync += [
                self.i.eq(Cat([ti.i for ti in self.t])),
                Cat([ti.o for ti in self.t]).eq(self.outs.storage | self.o),
                Cat([ti.oe for ti in self.t]).eq(self.oes.storage),
            ]
    return SimGpio

def create_sim_pitaya_ps():
    class SimPitayaPS(PitayaPS):
        def __init__(self, cpu):
            super().__init__(cpu)
            self.specials = []
            self.sync += [
                self.fclk.eq(self.fclk + 1),
                self.frstn.eq(1),
            ]
    return SimPitayaPS

def create_sim_scopegen():
    class SimScopeGen(ScopeGen):
        def __init__(self, width=25):
            super().__init__(width)
            self.specials = []
            self.sync += [
                self.writing_data_now.eq(~self.writing_data_now),
                self.scope_written_data.eq(self.scope_written_data + 1),
                self.scope_position.eq(self.scope_position + 1),
            ]
    return SimScopeGen

def create_sim_xadc():
    class SimXADC(XADC):
        def __init__(self, xadc):
            super().__init__(xadc)
            self.specials = []
            self.sync += [
                self.temp.status.eq(self.temp.status + 1),
                self.v.status.eq(self.v.status + 1),
                self.a.status.eq(self.a.status + 1),
                self.b.status.eq(self.b.status + 1),
                self.c.status.eq(self.c.status + 1),
                self.d.status.eq(self.d.status + 1),
            ]
    return SimXADC


class DummyADC:
    def __init__(self):
        self.cdcs = Signal()
        self.clk = Signal(2)
        self.data_a = Signal(14)
        self.data_b = Signal(14)

class DummyDAC:
    def __init__(self):
        self.rst = Signal()
        self.clk = Signal()
        self.wrt = Signal()
        self.sel = Signal()
        self.data = Signal(14)

class DummyXADC:
    def __init__(self):
        self.n = [Signal() for _ in range(5)]
        self.p = [Signal() for _ in range(5)]

class DummyCPU:
    def __init__(self):
        self.mio = Signal(54)
        self.ps_clk = Signal()
        self.ps_porb = Signal()
        self.ps_srstb = Signal()
        self.ddr_vrn = Signal()
        self.ddr_vrp = Signal()
        self.DDR_addr = Signal(15)
        self.DDR_ba = Signal(3)
        self.DDR_cas_n = Signal()
        self.DDR_ck_n = Signal()
        self.DDR_ck_p = Signal()
        self.DDR_cke = Signal()
        self.DDR_cs_n = Signal()
        self.DDR_dm = Signal(4)
        self.DDR_dq = Signal(32)
        self.DDR_dqs_n = Signal(4)
        self.DDR_dqs_p = Signal(4)
        self.DDR_odt = Signal()
        self.DDR_ras_n = Signal()
        self.DDR_reset_n = Signal()
        self.DDR_we_n = Signal()

class DummyExp:
    def __init__(self):
        self.n = Signal(8)
        self.p = Signal(8)

class DummyPlatform:
    def __init__(self):
        self.device = "xc7z010"
        self.resources = {
            "adc": DummyADC(),
            "dac": DummyDAC(),
            "xadc": DummyXADC(),
            "clk125": Signal(),
            "cpu": DummyCPU(),
            "exp": DummyExp(),
            "user_led": [Signal() for _ in range(8)],
            "pwm": [Signal() for _ in range(4)],
            "sata": [
                Record([("rx_p", 1), ("rx_n", 1), ("tx_p", 1), ("tx_n", 1)])
                for _ in range(2)
            ],
        }

    def request(self, resource, *args, **kwargs):
        if resource in self.resources:
            if isinstance(self.resources[resource], list):
                return self.resources[resource][args[0] if args else 0]
            return self.resources[resource]
        else:
            return Signal()

    def add_period_constraint(self, *args, **kwargs):
        pass

    def add_platform_command(self, *args, **kwargs):
        pass

def create_dummy_platform():
    return DummyPlatform()



def create_sim_linien_module():
    class SimLinienModule(LinienModule):
        def __init__(self, platform):
            super().__init__(platform)

        def init_submodules(self, width, signal_width, coeff_width, chain_factor_bits, platform):
            super().init_submodules(width, signal_width, coeff_width, chain_factor_bits, platform)
            
            # Replace hardware-specific modules with simulated versions
            self.submodules.analog = create_sim_pitaya_analog()(
                platform.request("adc"), platform.request("dac")
            )
            self.submodules.xadc = create_sim_xadc()(platform.request("xadc"))
            self.submodules.crg = create_sim_crg()(
                platform.request("clk125"), self.ps.fclk[0], ~self.ps.frstn[0]
            )
            self.submodules.dna = create_sim_dna()()
            self.submodules.gpio_n = create_sim_gpio()(platform.request("exp").n)
            self.submodules.gpio_p = create_sim_gpio()(platform.request("exp").p)
            self.submodules.ps = create_sim_pitaya_ps()(platform.request("cpu"))
            self.submodules.scopegen = create_sim_scopegen()()

    return SimLinienModule



def testbench(dut):
    ####################################### Set the CSR registers #############################################
    yield dut.limit_error_signal.max.storage.eq(1000)
    # Set the amplitude to 1/4 of the maximum value
    yield dut.mod.amp.storage.eq(1 << (14 - 2))
    # Set the frequency to 1/8 of the maximum value
    yield dut.mod.freq.storage.eq(0x10000000 // 8)
    # Set the modulation depth
    yield dut.mod.mod_depth.storage.eq(0x4000) #A000
    # Set the modulation frequency
    yield dut.mod.mod_freq.storage.eq(0x1000000)
    yield

    ###################### Dynamically change the Linien Module to replace any submodules that run hardware specific features that can't be simulated

    ###################### Set any initial output signals from the submodules


    ############################################# Run the simulation for 100 clock cycles #########################################
    for cycle in range(10):
        # Iterate through input/submodule signals and update the module with the new input

        # Probe and print some interesting signals from TestModule, that will update when the sync logic or inputs change with the new clock cycle 
        adc_a = yield dut.analog.adc_a
        dac_a = yield dut.analog.dac_a
        dac_b = yield dut.analog.dac_b
        
        print(f"Cycle {cycle}:")
        print(f"  ADC A: {adc_a}")
        print(f"  DAC A: {dac_a}")
        print(f"  DAC B: {dac_b}")

        # Access signals from submodules
        pid_running = yield dut.logic.pid.running
        sweep_y = yield dut.logic.sweep.y
        autolock_status = yield dut.logic.autolock.lock_running.status
        fast_a_out = yield dut.fast_a.out_i
        
        print(f"  PID Running: {pid_running}")
        print(f"  Sweep Y: {sweep_y}")
        print(f"  Autolock Status: {autolock_status}")
        print(f"  Fast Chain A Out: {fast_a_out}")
        
        # Access some CSR values
        dual_channel = yield dut.logic.dual_channel.storage
        mod_channel = yield dut.logic.mod_channel.storage
        control_channel = yield dut.logic.control_channel.storage
        
        print(f"  Dual Channel: {dual_channel}")
        print(f"  Mod Channel: {mod_channel}")
        print(f"  Control Channel: {control_channel}")
        
        # Advance the clock
        yield

# Run the testbench against the LinienModule
if __name__ == "__main__":
    dummy_platform = create_dummy_platform()
    platform = Platform()
    SimLinienModule = create_sim_linien_module()
    dut = SimLinienModule(dummy_platform)
    run_simulation(dut, testbench(dut), vcd_name="linien_module.vcd")
