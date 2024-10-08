import numpy as np

def generate_sine_wave(filename="C:\\linien_2ndmod\\gateware_1chain\\cocotb\\lut.init", size=1024, width=16):
    """
    Generate a sine wave LUT and write to a file in Verilog-readable format.
    
    :param filename: The name of the file to write the LUT to.
    :param size: The number of addresses in the LUT.
    :param width: The bit-width of each LUT value (signed).
    """
    # Generate a quarter wave sine
    quarter_wave = np.sin(np.pi * np.arange(size // 4) / (size // 4))
    max_val = 2**15 - 1  # Maximum 16-bit signed value
    quarter_wave_int = (quarter_wave * max_val).astype(np.int16)

    # Mirror the quarter wave to get a full sine wave
    full_wave = np.concatenate([quarter_wave_int, -quarter_wave_int[::-1], -quarter_wave_int, quarter_wave_int[::-1]])

    with open(filename, 'w') as f:
        for value in full_wave:
            f.write(f"{value & ((1 << width) - 1):04X}\n")
