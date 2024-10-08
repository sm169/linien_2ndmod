from migen import *
from ..linien_module import LinienLogic

def input_signal():
    # Produces a signal that can be interated through in testbench to simulate input to the linien module
    pass

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

        # Probe and print some interesting signals from LinienLogic, that will update when the sync logic or inputs change with the new clock cycle 
        dual_channel = yield dut.dual_channel.storage
        mod_channel = yield dut.mod_channel.storage
        control_channel = yield dut.control_channel.storage
        pid_only_mode = yield dut.pid_only_mode.storage
        chain_a_factor = yield dut.chain_a_factor.storage
        chain_a_offset = yield dut.chain_a_offset.storage
        
        print(f"Cycle {cycle}:")
        print(f"  Dual Channel: {dual_channel}")
        print(f"  Mod Channel: {mod_channel}")
        print(f"  Control Channel: {control_channel}")
        print(f"  PID Only Mode: {pid_only_mode}")
        print(f"  Chain A Factor: {chain_a_factor}")
        print(f"  Chain A Offset: {chain_a_offset}")

        if cycle%2 == 0:
            yield dut.limit_error_signal.x.eq(2000)
        # You can also access and print signals from submodules
        sweep_y = yield dut.sweep.y
        pid_running = yield dut.pid.running
        autolock_status = yield dut.autolock.lock_running.status
        signal = yield dut.signal_out
        mod = yield dut.mod.fm_wave
        
        print(f"  Sweep Y: {sweep_y}")
        print(f"  PID Running: {pid_running}")
        print(f"  Autolock Status: {autolock_status}")
        print(f"  Signal Out: {signal}")
        print(f"  Mod: {mod}")
        
        # Advance the clock
        yield

# Run the testbench against the LinienLogic module
if __name__ == "__main__":
    dut = LinienLogic()
    run_simulation(dut, testbench(dut), vcd_name="linien_logic.vcd")
