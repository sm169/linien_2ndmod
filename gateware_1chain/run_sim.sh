#!/bin/bash

# Activate the conda environment
#conda activate rpclone

# Set the Migen and Cocotb paths if needed (optional)
export PYTHONPATH=.:$PYTHONPATH

# Convert Migen design to Verilog
python -m logic.convert_to_verilog

# Run the simulation using make (invokes the Makefile)
cd cocotb
make SIM=icarus
