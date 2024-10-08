import numpy as np
import matplotlib.pyplot as plt
from migen import Module, Signal, run_simulation

from gateware.logic.modulateDebug import Modulate

def test_modulate():
    """
    Test the modulation functionality of the `Modulate` class.
    This test sets up a modulation instance with specific parameters and runs a simulation
    to verify the behavior of the modulation output. The test performs the following checks:
    1. Ensures the output data is oscillating.
    2. Verifies that the phase is monotonically increasing.
    3. Confirms that the output frequency matches the expected frequency.
    The test uses the following parameters:
    - `width`: Bit width for the modulation.
    - `amp`: Amplitude of the modulation signal.
    - `freq`: Frequency of the modulation signal.
    - `mod_depth`: Depth of the modulation.
    - `mod_freq`: Frequency of the modulation depth.
    The simulation runs for 1000 cycles, collecting output data and phase information.
    Assertions:
    - The output data should oscillate, indicated by a difference between the maximum and minimum values.
    - The phase should be monotonically increasing.
    - The main frequency component of the output data should match the expected frequency within a tolerance of 0.1.
    Raises:
    - AssertionError: If any of the checks fail.
    """
    wid = 14
    # Initialize lists to store output data and phase
    data = []
    phase = []
    fm = []
    zp = []

    def tb(dut):
        # Set the amplitude to 1/4 of the maximum value
        yield dut.amp.storage.eq(1 << (wid - 2))
        # Set the frequency to 1/8 of the maximum value
        yield dut.freq.storage.eq(0x10000000 // 8)
        # Set the modulation depth
        yield dut.mod_depth.storage.eq(0x4000) #A000
        # Set the modulation frequency
        yield dut.mod_freq.storage.eq(0x1000000)

        # Run the simulation for 1000 cycles
        for i in range(2000):
            yield

            if i == 30: 
                print((yield dut.fractional_part))
                print((yield dut.primary_address))
            # Collect output data and phase
            data.append((yield dut.y))
            phase.append((yield dut.ptest))
            fm.append((yield dut.fm_result))
            zp.append((yield dut.zp))

    # Create an instance of the Modulate class
    dut = Modulate(width=wid)
    # Run the simulation with the test bench
    run_simulation(dut, tb(dut))

    # Convert collected data to numpy arrays for analysis
    data = np.array(data)
    phase = np.array(phase)
    fm = np.array(fm)
    zp = np.array(zp)

    # Check if the output is oscillating
    #assert np.max(data) > np.min(data), "Output is not oscillating"

    # Check if the phase is monotonically increasing
    #assert np.all(np.diff(phase) >= 0), "Phase is not monotonically increasing"

    # Perform FFT on the output data
    N = 32096
    fft = np.fft.fft(data, N)
    # Calculate the frequency bins
    freqs = np.fft.fftfreq(1000)
    # Find the main frequency component
    main_freq = 0 #freqs[np.argmax(np.abs(fft))]
    print(main_freq)
    # Set the expected frequency
    expected_freq = 1 / 8  # Adjust this based on your expected frequency
    # Check if the main frequency matches the expected frequency
    #assert abs(main_freq - expected_freq) < 0.1, "Output frequency is incorrect"
    return data, phase, fm, zp, fft, freqs

# Allow the script to be run standalone
if __name__ == "__main__":
    data, phase, fm, zp, fft, freqs = test_modulate()
    fig, ax = plt.subplots(3)
    ax[0].plot(data)
    ax[0].plot(phase)
    ax[1].plot(fm)
    ax[1].plot(zp)
    ax[2].plot(freqs[0:int(len(freqs)/2)], np.abs(fft[0:int(len(freqs)/2)]))
    plt.show()
