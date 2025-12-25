#!/bin/bash
# Vivado Simulator Run Script
# Usage: ./run_vivado.sh [options]

set -e

DUT="${1:-simple_dut.v}"
TESTBENCH_DIR="${2:-generated_tb}"
TOP_MODULE="${3:-tb}"
SEED="${4:-1}"
GUI_MODE="${5:-0}"

echo "[VIVADO] SystemVerilog/UVM Simulation Runner"
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

# Create work directory
mkdir -p work

# Collect source files
SOURCES="$DUT"
for sv_file in "$TESTBENCH_DIR"/*.sv; do
    SOURCES="$SOURCES $sv_file"
done

echo "[VIVADO] Compilation Phase..."
COMPILE_CMD="xvlog -sv --work work --timescale 1ns/1ps"
COMPILE_CMD="$COMPILE_CMD $SOURCES"

echo "[VIVADO] Command: $COMPILE_CMD"
eval $COMPILE_CMD

if [ $? -ne 0 ]; then
    echo "[ERROR] Vivado compilation failed"
    exit 1
fi

echo "[VIVADO] Elaboration Phase..."
ELAB_CMD="xelab --work work $TOP_MODULE"

echo "[VIVADO] Command: $ELAB_CMD"
eval $ELAB_CMD

if [ $? -ne 0 ]; then
    echo "[ERROR] Vivado elaboration failed"
    exit 1
fi

echo "[VIVADO] Simulation Phase..."

RUN_CMD="xsim work/$TOP_MODULE"
RUN_CMD="$RUN_CMD +UVM_VERBOSITY=UVM_HIGH"
RUN_CMD="$RUN_CMD -l vivado_simulation.log"

if [ $GUI_MODE -eq 1 ]; then
    RUN_CMD="$RUN_CMD -gui"
fi

echo "[VIVADO] Command: $RUN_CMD"
eval $RUN_CMD

echo "[VIVADO] Simulation Complete!"
echo "[VIVADO] Log file: vivado_simulation.log"
