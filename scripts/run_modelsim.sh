#!/bin/bash
# Modelsim Simulator Run Script
# Usage: ./run_modelsim.sh [options]

set -e

DUT="${1:-simple_dut.v}"
TESTBENCH_DIR="${2:-generated_tb}"
TOP_MODULE="${3:-tb}"
SEED="${4:-1}"
GUI_MODE="${5:-0}"

echo "[MODELSIM] SystemVerilog/UVM Simulation Runner"
echo "================================================"
echo "DUT:              $DUT"
echo "Testbench Dir:    $TESTBENCH_DIR"
echo "Top Module:       $TOP_MODULE"
echo "Random Seed:      $SEED"
echo "GUI Mode:         $([ $GUI_MODE -eq 1 ] && echo 'Yes' || echo 'No')"
echo "================================================"

# Check if DUT exists
if [ ! -f "$DUT" ]; then
    echo "[ERROR] DUT file not found: $DUT"
    exit 1
fi

# Check if testbench directory exists
if [ ! -d "$TESTBENCH_DIR" ]; then
    echo "[ERROR] Testbench directory not found: $TESTBENCH_DIR"
    exit 1
fi

# Create library
echo "[MODELSIM] Creating work library..."
vlib work
vmap work work

# Collect source files
SOURCES="$DUT"
for sv_file in "$TESTBENCH_DIR"/*.sv; do
    SOURCES="$SOURCES $sv_file"
done

echo "[MODELSIM] Compilation Phase..."
COMPILE_CMD="vlog -sv -work work -timescale=1ns/1ps"
COMPILE_CMD="$COMPILE_CMD $SOURCES"

echo "[MODELSIM] Command: $COMPILE_CMD"
eval $COMPILE_CMD

if [ $? -ne 0 ]; then
    echo "[ERROR] Modelsim compilation failed"
    exit 1
fi

echo "[MODELSIM] Elaboration and Simulation Phase..."

if [ $GUI_MODE -eq 1 ]; then
    RUN_CMD="vsim -work work -sv_seed $SEED"
    RUN_CMD="$RUN_CMD +UVM_VERBOSITY=UVM_HIGH"
    RUN_CMD="$RUN_CMD -gui $TOP_MODULE"
else
    RUN_CMD="vsim -work work -sv_seed $SEED"
    RUN_CMD="$RUN_CMD +UVM_VERBOSITY=UVM_HIGH"
    RUN_CMD="$RUN_CMD -c -do 'run -all; quit' $TOP_MODULE"
    RUN_CMD="$RUN_CMD -l modelsim_simulation.log"
fi

echo "[MODELSIM] Command: $RUN_CMD"
eval $RUN_CMD

echo "[MODELSIM] Simulation Complete!"
[ $GUI_MODE -eq 0 ] && echo "[MODELSIM] Log file: modelsim_simulation.log"
