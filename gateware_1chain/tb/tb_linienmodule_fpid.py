from migen import *
from migen.fhdl import verilog
from ..linien_module import LinienModule
from ..hw_platform import DummyPlatform

import numpy as np
import matplotlib.pyplot as plt

class TestBench(Module):
    def __init__(self):
        self.platform = DummyPlatform()
        self.submodules.dut = LinienModule(self.platform)

        # Define the sys_double clock domain with a reset as well

        # define cl125 as well and make sure that ps signal given to CRG doesn't override sys_ps

        
        # Optional: print the available clock domains for debugging
        print(self.dut.clock_domains)  # List available clock domains before simulation

    def do_simulation(self):
        carrier_address_values = []
        carrier_wave_values = []
        mod_address_values = []
        mod_wave_values = []
        fm_wave_values = []
        # Simulate for 1000 cycles
        yield self.dut.logic.mod.freq.storage.eq(0x0FFFFFFF)
        yield self.dut.logic.mod.mod_depth.storage.eq(0x4000)
        yield self.dut.logic.mod.mod_freq.storage.eq(0x5000)
        yield self.dut.analog.adc_b.eq(0x3FFF)
        yield self.dut.analog.adc_a.eq(0x3FFF)

        yield self.dut.logic.mod.f_pid_status.storage.eq(1)

       # yield self.dut.logic.pid.kp.storage.eq(0x2EFF)  # Set proportional gain
       
        yield self.dut.logic.pid_only_mode.storage.eq(1)  # Set proportional gain
        
        yield self.dut.logic.fp.ki.storage.eq(0x2000)   # Set integral gain
        yield self.dut.logic.fp.kd.storage.eq(0)    # Set derivative gain
        yield self.dut.logic.fp.setpoint.storage.eq(0x0000)  # Set setpoint
        yield self.dut.logic.fp.running.eq(1)  # Set setpoint
        yield self.dut.logic.pid.running.eq(1)  # Set setpoint

        yield


        for i in range(20):
            # Toggle the primary clock

            '''if i < 10:
                yield self.dut.logic.mod.f_pid_on.eq(1)
            else:
                yield self.dut.logic.mod.f_pid_on.eq(0)'''

            yield self.dut.logic.fp.kp.storage.eq(0x2EFF)  # Set proportional gain

            yield
            yield        
            # Apply test vectors to fast chain inputs
            #yield self.dut.fast_a.adc.eq(i % 256)  # Example input

            # Check outputs of modulate, filter, and limit modules
            carrier_address = yield self.dut.logic.mod.carrier_phase
            carrier_address_values.append(carrier_address)

            carrier_wave = yield self.dut.logic.mod.carrier_wave
            carrier_wave_values.append(carrier_wave)

            mod_address = yield self.dut.logic.mod.mod_phase
            mod_address_values.append(mod_address)

            mod_wave = yield self.dut.logic.mod.mod_wave
            mod_wave_values.append(mod_wave)

            modulate_out = yield self.dut.logic.mod.fm_wave
            fm_wave_values.append(modulate_out)

            filter_out = yield self.dut.fast_a.iir_c_1.y
            limit_out = yield self.dut.logic.limit_fast1.y

            fpid_out = yield self.dut.logic.fp.output_p

            fv = yield self.dut.logic.mod.freq_var

            print(f"Cycle {i}: Input={i % 256}, freq_var={fv}, pid={fpid_out}, wave={carrier_wave}")

            yield

        '''# Plot the signals
        fig, axs = plt.subplots(3, 2, figsize=(15, 15))
        fig.suptitle('Carrier, Mod, and FM Wave Signals')

        axs[0, 0].plot(carrier_address_values)
        axs[0, 0].set_title('Carrier Address')
        axs[0, 0].set_xlabel('Clock Cycles')
        axs[0, 0].set_ylabel('Address')
        axs[0, 0].grid(True)

        axs[0, 1].plot(carrier_wave_values)
        axs[0, 1].set_title('Carrier Wave')
        axs[0, 1].set_xlabel('Clock Cycles')
        axs[0, 1].set_ylabel('Amplitude')
        axs[0, 1].grid(True)

        axs[1, 0].plot(mod_address_values)
        axs[1, 0].set_title('Mod Address')
        axs[1, 0].set_xlabel('Clock Cycles')
        axs[1, 0].set_ylabel('Address')
        axs[1, 0].grid(True)

        axs[1, 1].plot(mod_wave_values)
        axs[1, 1].set_title('Mod Wave')
        axs[1, 1].set_xlabel('Clock Cycles')
        axs[1, 1].set_ylabel('Amplitude')
        axs[1, 1].grid(True)

        axs[2, 0].plot(fm_wave_values)
        axs[2, 0].set_title('FM Wave')
        axs[2, 0].set_xlabel('Clock Cycles')
        axs[2, 0].set_ylabel('Amplitude')
        axs[2, 0].grid(True)

        axs[2, 1].axis('off')  # Remove the last unused subplot

        plt.tight_layout()
        plt.savefig('wave_plots_new.png')'''

def test_linien_module():
    tb = TestBench()
    run_simulation(tb.dut,
                    tb.do_simulation(),
                    clocks={"sys": 16,
                            "sys_double": 8,
                            "sys_slow": 240,
                            "sys_ps": 8
                            },
                    vcd_name="test_linien_module.vcd")

if __name__ == "__main__":
    test_linien_module()
