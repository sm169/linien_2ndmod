import cocotb
from cocotb.triggers import Timer
import matplotlib.pyplot as plt

@cocotb.test()
async def fm_wave_test(dut):
    """Test that plots the carrier, mod, and fm wave signals"""
    dut._log.info("Starting the wave test...")
    
    # Initialize signals with hexadecimal values
    dut.sys_rst.value = 0x1
    dut.freq_storage.value = 0x00FFFFFF  
    dut.mod_depth_storage.value = 0x4000
    dut.mod_freq_storage.value = 0x5000
    #print(f.n_bits)

    # Define clock period
    clock_period = 10  # 10 ns

    # Function to generate clock
    async def generate_clock():
        while True:
            dut.sys_clk.value = 0
            await Timer(clock_period // 2, units='ns')
            dut.sys_clk.value = 1
            await Timer(clock_period // 2, units='ns')

    # Start the clock
    cocotb.start_soon(generate_clock())

    # Wait for a few clock cycles and then de-assert reset
    for _ in range(5):
        await Timer(clock_period, units='ns')
    dut.sys_rst.value = 0x0

    carrier_address_values = []
    carrier_wave_values = []
    mod_address_values = []
    mod_wave_values = []
    fm_wave_values = []
    
    # Collect values for 1000 clock cycles
    for _ in range(1000):
        await Timer(clock_period, units='ns')
        carrier_address_values.append(dut.carrier_address.value.integer)
        carrier_wave_values.append(dut.carrier_wave.value.signed_integer)
        mod_address_values.append(dut.mod_address.value.integer)
        mod_wave_values.append(dut.mod_wave.value.signed_integer)
        fm_wave_values.append(dut.fm_wave.value.signed_integer)

    # Plot the signals
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
    plt.savefig('wave_plots.png')
    
    dut._log.info("Wave test completed. Plots saved as wave_plots.png")
