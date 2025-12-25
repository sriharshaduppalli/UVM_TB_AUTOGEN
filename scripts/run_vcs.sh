#!/bin/bash
# VCS Simulator Run Script
# Usage: ./run_vcs.sh [options]

set -e

DUT="${1:-simple_dut.v}"
TESTBENCH_DIR="${2:-generated_tb}"
TOP_MODULE="${3:-tb}"
SEED="${4:-1}"
GUI_MODE="${5:-0}"

echo "[VCS] SystemVerilog/UVM Simulation Runner"
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

echo "[VCS] Compilation Phase..."
COMPILE_CMD="vcs -full64 -sverilog -assert svaext -timescale=1ns/1ps +v2k"
COMPILE_CMD="$COMPILE_CMD -top $TOP_MODULE"
COMPILE_CMD="$COMPILE_CMD -ntb_random_seed $SEED"

if [ $GUI_MODE -eq 1 ]; then
    COMPILE_CMD="$COMPILE_CMD -gui"
fi

COMPILE_CMD="$COMPILE_CMD $SOURCES"

echo "[VCS] Command: $COMPILE_CMD"
eval $COMPILE_CMD

if [ $? -ne 0 ]; then
    echo "[ERROR] VCS compilation failed"
    exit 1
fi

echo "[VCS] Elaboration and Simulation Phase..."
RUN_CMD="./simv +UVM_VERBOSITY=UVM_HIGH"
RUN_CMD="$RUN_CMD -l vcs_simulation.log"

if [ $GUI_MODE -eq 1 ]; then
    RUN_CMD="$RUN_CMD -gui"
fi

echo "[VCS] Command: $RUN_CMD"
eval $RUN_CMD

echo "[VCS] Simulation Complete!"
echo "[VCS] Log file: vcs_simulation.log"
