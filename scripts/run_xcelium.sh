#!/bin/bash
# Xcelium Simulator Run Script
# Usage: ./run_xcelium.sh [options]

set -e

DUT="${1:-simple_dut.v}"
TESTBENCH_DIR="${2:-generated_tb}"
TOP_MODULE="${3:-tb}"
SEED="${4:-1}"
GUI_MODE="${5:-0}"

echo "[XCELIUM] SystemVerilog/UVM Simulation Runner"
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

# Collect source files
SOURCES="$DUT"
for sv_file in "$TESTBENCH_DIR"/*.sv; do
    SOURCES="$SOURCES $sv_file"
done

echo "[XCELIUM] Compilation and Elaboration Phase..."

RUN_CMD="xrun -elaborate -64bit -sv"
RUN_CMD="$RUN_CMD -timescale 1ns/1ps"
RUN_CMD="$RUN_CMD -top $TOP_MODULE"
RUN_CMD="$RUN_CMD -random_seed $SEED"
RUN_CMD="$RUN_CMD +UVM_VERBOSITY=UVM_HIGH"
RUN_CMD="$RUN_CMD -l xcelium_simulation.log"

if [ $GUI_MODE -eq 1 ]; then
    RUN_CMD="$RUN_CMD -gui"
fi

RUN_CMD="$RUN_CMD $SOURCES"

echo "[XCELIUM] Command: $RUN_CMD"
eval $RUN_CMD

if [ $? -ne 0 ]; then
    echo "[ERROR] Xcelium simulation failed"
    exit 1
fi

echo "[XCELIUM] Simulation Complete!"
echo "[XCELIUM] Log file: xcelium_simulation.log"
