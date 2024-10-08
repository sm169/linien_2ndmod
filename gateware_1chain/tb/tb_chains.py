from migen import *
from migen.fhdl import verilog
from ..linien_module import LinienModule
from ..hw_platform import Platform


class TestLinienModule(Module):
    def __init__(self):
        self.submodules.dut = LinienModule(platform=Platform())

    def test_single_chain(self):
        def tb(dut):
            # Test single chain mode
            yield dut.logic.dual_channel.storage.eq(0)
            yield dut.logic.chain_a_factor.storage.eq(1 << 7)  # Set to 1.0
            yield dut.logic.chain_a_offset.storage.eq(100)
            yield dut.analog.adc_a.eq(1000)
            yield
            
            # Check if the mixed signal is correct
            mixed = yield dut.logic.limit_error_signal.x
            assert mixed == 1100, f"Expected mixed signal 1100, got {mixed}"

            # Test with different chain factor
            yield dut.logic.chain_a_factor.storage.eq(1 << 6)  # Set to 0.5
            yield
            mixed = yield dut.logic.limit_error_signal.x
            assert mixed == 600, f"Expected mixed signal 600, got {mixed}"

            # Test dual channel mode (should behave the same as single channel)
            yield dut.logic.dual_channel.storage.eq(1)
            yield
            mixed = yield dut.logic.limit_error_signal.x
            assert mixed == 600, f"Expected mixed signal 600, got {mixed}"

            print("All tests passed!")

        run_simulation(self, tb(self.dut), vcd_name="test_linien_module.vcd")

if __name__ == "__main__":
    test = TestLinienModule()
    test.test_single_chain()
