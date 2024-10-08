from migen import *
from migen.fhdl import verilog
from ..linien_module import LinienModule, LinienLogic
from ..hw_platform import DummyPlatform

import matplotlib.pyplot as plt

def test_linien_module():
    def tb(dut):
        # Set up initial conditions
        carrier_wave_values = []

        logic = dut.logic
        yield logic.mod.freq.storage.eq(0x0FFFFFFF)
        yield logic.mod.mod_depth.storage.eq(0x4000)
        yield logic.mod.mod_freq.storage.eq(0x5000)
        yield dut.analog.dummyadc.eq(0x0200)
        #yield dut.analog.adc_a.eq(0x3FFF)
        yield logic.mod.f_pid_status.storage.eq(1)
        #yield logic.pid_only_mode.storage.eq(1)
        
        # Set PID parameters
        yield logic.fp.kp.storage.eq(0x1EFF)
        yield logic.fp.ki.storage.eq(0x0000)
        yield logic.fp.kd.storage.eq(0)
        yield logic.fp.setpoint.storage.eq(0x0000)
        #yield logic.fp.input.eq(0x0000)
        yield logic.fp.running.eq(1)
        #yield logic.pid.running.eq(1)

        yield

        for i in range(100):
            if i == 50:
                yield dut.analog.dummyadc.eq(0x0F00)
                yield
            carrier_address = yield logic.mod.carrier_phase
            adc = yield dut.analog.adc_b
            carrier_wave = yield logic.mod.carrier_wave
            carrier_wave_values.append(carrier_wave)
            mod_address = yield logic.mod.mod_phase
            mod_wave = yield logic.mod.mod_wave
            modulate_out = yield logic.mod.fm_wave
            #filter_out = yield dut.fast_a.iir_c_1.y
            limit_out = yield logic.limit_fast1.y
            fpid_out = yield logic.fp.pid_out
            fv = yield logic.mod.freq_var

            print(f"Cycle {i}: freq_var={fv}, pid={fpid_out}, wave={carrier_wave}, adc_b={adc}")

            yield

        plt.plot(carrier_wave_values)
        plt.title('Carrier Wave')
        plt.xlabel('Clock Cycles')
        plt.ylabel('Amplitude')
        plt.show()

    platform = DummyPlatform()
    dut = LinienModule(platform)
    #dut = LinienLogic()
    run_simulation(dut, tb(dut), 
                   clocks={"sys": 16, "sys_double": 8, "sys_slow": 240, "sys_ps": 8},
                   vcd_name="test_linien_module.vcd")

if __name__ == "__main__":
    test_linien_module()
