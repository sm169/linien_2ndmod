from migen import *
from misoc.interconnect.csr import AutoCSR, CSRStorage
from migen.fhdl.specials import Memory
from migen.fhdl.bitcontainer import log2_int, bits_for

import numpy as np

from .cordic import Cordic
from .filter import Filter


class Demodulate(Module, AutoCSR):
    """
    Demodulate Module
    This module performs demodulation of an input signal using a CORDIC algorithm.
    Attributes:
        x (Signal): Input signal of specified width.
        i (Signal): Demodulated in-phase signal of specified width.
        q (Signal): Demodulated quadrature-phase signal of specified width.
        delay (CSRStorage): Control and status register for delay, with a width of `freq_width`.
        multiplier (CSRStorage): Control and status register for multiplier, with a width of 4 and a default reset value of 1.
        phase (Signal): Signal representing the phase with the specified width.
        cordic (Cordic): Submodule implementing the CORDIC algorithm with specified parameters.
    Args:
        freq_width (int): Width of the frequency-related signals. Default is 32.
        width (int): Width of the input and demodulated signals. Default is 14.
    Comb Logic:
        - The input signal `x` is fed into the CORDIC module.
        - The phase is calculated using the formula: 
          `((phase * multiplier.storage) + delay.storage) << 1`
        - The demodulated in-phase (`i`) and quadrature-phase (`q`) signals are obtained from the CORDIC module outputs and right-shifted by 1.
    """
    def __init__(self, freq_width=32, width=14):
        # input signal
        
        self.x = Signal((width, True))

        # demodulated signals (i and q)
        self.i = Signal((width, True))
        self.q = Signal((width, True))

        self.delay = CSRStorage(freq_width)
        self.multiplier = CSRStorage(4, reset=1)
        self.phase = Signal(width)

        self.submodules.cordic = Cordic(
            width=width + 1,
            stages=width + 1,
            guard=2,
            eval_mode="pipelined",
            cordic_mode="rotate",
            func_mode="circular",
        )

        self.comb += [
            # cordic input
            self.cordic.xi.eq(self.x),
            self.cordic.zi.eq(
                ((self.phase * self.multiplier.storage) + self.delay.storage) << 1
            ),
            # cordic output
            self.i.eq(self.cordic.xo >> 1),
            self.q.eq(self.cordic.yo >> 1),
        ]


class Modulate(Module):
    def __init__(self, freq_width=32, lut_size=1024, **kwargs):
        # Set up registers and signals
        
        
        width = 16  # Width for the sine wave samples
        address_bits = log2_int(lut_size) - 1  # Number of address bits for the LUT

        # Control registers
        self.amp = CSRStorage(width)           # Amplitude control
        self.freq = CSRStorage(freq_width)     # Carrier frequency control
        self.mod_depth = CSRStorage(width+2)   # Modulation depth control
        self.mod_freq = CSRStorage(freq_width) # Modulation frequency control
        self.f_pid_status = CSRStorage()

        self.f_pid_on = Signal()
        self.comb += self.f_pid_on.eq(self.f_pid_status.storage)

        # Phase accumulators
        self.carrier_phase = Signal(freq_width)
        self.mod_phase = Signal(freq_width)

        # signal for 1st freq
        self.freq_var = Signal(freq_width, name="freq_var")
        self.pid_in = Signal((freq_width-4,True))

        # set signals for exposing
        self.state_in = []
        self.state_out = []
        self.signal_in = []
        self.signal_out = self.freq_var

        self.comb += [
            If(self.f_pid_on,self.freq_var.eq(self.freq.storage + self.pid_in))
            .Else(self.freq_var.eq(self.freq.storage))
        ]
        
        # Signals for outputs
        self.carrier_wave = Signal((16, True))  # Carrier wave output
        self.mod_wave = Signal((16, True))      # Modulating wave output
        self.fm_wave = Signal((16, True))       # FM-modulated wave output

        # Define a memory block for the sine LUT (16-bit signed, LUT size entries)
        self.lut = Memory(width=16, depth=lut_size, init=self.generate_quarter_wave_sine(lut_size))
        # Create multiple read ports
        carrier_lut_rdport = self.lut.get_port()
        mod_lut_rdport = self.lut.get_port()
        fm_lut_rdport = self.lut.get_port()

        # Add the LUT and ports to the module's specials
        self.specials += self.lut, carrier_lut_rdport, mod_lut_rdport, fm_lut_rdport

        # Create the logic for the carrier and modulation phase accumulation
        self.sync += [
            self.carrier_phase.eq(self.carrier_phase + self.freq_var),  # Carrier phase accumulation
            self.mod_phase.eq(self.mod_phase + self.mod_freq.storage)       # Modulation phase accumulation
        ]

        # Create the combined FM phase (carrier + modulation)
        combined_phase = Signal(freq_width)
        self.comb += [
            combined_phase.eq(self.carrier_phase + (self.mod_wave * self.mod_depth.storage))
        ]

        # Address generation for LUT
        carrier_address = Signal(address_bits)
        mod_address = Signal(address_bits)
        fm_address = Signal(address_bits)

        self.comb += [
            carrier_address.eq(self.carrier_phase[-address_bits:]),   # MSBs of carrier phase for LUT address
            mod_address.eq(self.mod_phase[-address_bits:]),           # MSBs of mod phase for LUT address
            fm_address.eq(combined_phase[-address_bits:])             # MSBs of combined FM phase for LUT address
        ]

        # LUT lookup for carrier, modulating, and FM signals
        carrier_lut_out = Signal(16)
        mod_lut_out = Signal(16)
        fm_lut_out = Signal(16)

        # Carrier LUT access
        self.comb += [
            carrier_lut_rdport.adr.eq(carrier_address),
            carrier_lut_out.eq(carrier_lut_rdport.dat_r)  # Read carrier signal from LUT
        ]

        # Modulating wave LUT access
        self.comb += [
            mod_lut_rdport.adr.eq(mod_address),
            mod_lut_out.eq(mod_lut_rdport.dat_r)  # Read modulating signal from LUT
        ]

        # FM-modulated wave LUT access
        self.comb += [
            fm_lut_rdport.adr.eq(fm_address),
            fm_lut_out.eq(fm_lut_rdport.dat_r)  # Read FM signal from LUT
        ]

        # Apply quadrant logic for carrier, modulating, and FM waves
        self.apply_quadrants(self.carrier_phase, carrier_lut_out, self.carrier_wave)
        self.apply_quadrants(self.mod_phase, mod_lut_out, self.mod_wave)
        self.apply_quadrants(combined_phase, fm_lut_out, self.fm_wave)

    # Generate a quarter-wave sine table for the LUT
    def generate_quarter_wave_sine(self, lut_size):
        # Generate a sine wave (quarter wave)
        quarter_wave = np.sin(np.pi * np.arange(lut_size // 4) / (lut_size // 4))
        max_val = 2**15 - 1  # Maximum 16-bit signed value
        quarter_wave_int = (quarter_wave * max_val).astype(np.int16)  # Convert to signed 16-bit integer

        # Mirror the quarter wave to get a full sine wave
        full_wave = np.concatenate([quarter_wave_int, -quarter_wave_int[::-1], -quarter_wave_int, quarter_wave_int[::-1]])

        return full_wave.tolist()

    # Apply quadrant symmetry using Migen's combinatorial logic
    def apply_quadrants(self, phase, lut_sample, output_signal):
        # Extract the quadrant based on the most significant bits of the phase
        quadrant = Signal(2)  # 2 bits to represent the quadrant (00, 01, 10, 11)
        self.comb += quadrant.eq(phase[-1:])  # Get the two MSBs

        # Apply the appropriate quadrant transformation
        self.comb += If(quadrant == 0b00,
            output_signal.eq(lut_sample)  # First quadrant
        ).Elif(quadrant == 0b01,
            output_signal.eq(lut_sample)  # Second quadrant (same as first)
        ).Elif(quadrant == 0b10,
            output_signal.eq(-lut_sample)  # Third quadrant (negative)
        ).Else(
            output_signal.eq(-lut_sample)  # Fourth quadrant (negative)
        )
