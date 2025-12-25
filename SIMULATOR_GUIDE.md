# Industry Simulator Integration Guide

The UVM testbench generator produces **simulator-agnostic** SystemVerilog code that works with all industry-standard simulators. This guide explains how to use the generated testbenches with different tools.

## Supported Simulators

| Simulator | Vendor | Status | GUI | Seed Control |
|-----------|--------|--------|-----|--------------|
| **VCS** | Synopsys | ✅ Full | ✅ Yes | ✅ Yes |
| **Modelsim** | Mentor Graphics | ✅ Full | ✅ Yes | ✅ Yes |
| **Xcelium** | Cadence | ✅ Full | ✅ Yes | ✅ Yes |
| **Vivado Simulator** | Xilinx | ✅ Full | ✅ Yes | ⚠️ Limited |

---

## Quick Start: Python Runner

The easiest way to run simulations across all simulators:

```bash
# List available simulators on your system
python3 run_simulation.py --list

# Auto-detect and run with first available simulator
python3 run_simulation.py --dut examples/simple_dut.v \
                          --testbench gen_assertions \
                          --auto

# Run with specific simulator
python3 run_simulation.py --dut examples/simple_dut.v \
                          --testbench gen_assertions \
                          --simulator vcs \
                          --seed 12345

# Launch GUI mode
python3 run_simulation.py --dut examples/simple_dut.v \
                          --testbench gen_assertions \
                          --simulator modelsim \
                          --gui
```

### Options

- `--simulator` : Choose simulator (vcs, modelsim, xcelium, vivado)
- `--dut` : Path to DUT file (required)
- `--testbench` : Path to generated testbench directory (required)
- `--top` : Top module name (default: tb)
- `--gui` : Launch in GUI mode
- `--seed` : Set random seed for reproducibility
- `--auto` : Auto-detect available simulator
- `--list` : List installed simulators

---

## Make-Based Approach

For traditional workflows, use the provided Makefile:

### VCS (Synopsys)

```bash
# Compile with VCS
make -f Makefile.sim SIM=vcs compile

# Run simulation
make -f Makefile.sim SIM=vcs run

# Run with GUI
make -f Makefile.sim SIM=vcs gui SEED=123

# Clean artifacts
make -f Makefile.sim clean
```

**Generated files**: `simv`, `work`, `vcs_simulation.log`

### Modelsim (Mentor)

```bash
# Compile and elaborate
make -f Makefile.sim SIM=modelsim compile

# Run simulation
make -f Makefile.sim SIM=modelsim run

# Launch waveform viewer
make -f Makefile.sim SIM=modelsim gui

# Clean up
make -f Makefile.sim clean
```

**Generated files**: `work/`, `modelsim.ini`, `modelsim_simulation.log`

### Xcelium (Cadence)

```bash
# Compile and run (Xcelium handles this in one step)
make -f Makefile.sim SIM=xcelium run

# GUI mode with specific seed
make -f Makefile.sim SIM=xcelium gui SEED=42

# Clean
make -f Makefile.sim clean
```

**Generated files**: `xcelium.d/`, `xcelium_simulation.log`

### Vivado Simulator (Xilinx)

```bash
# Compile design
make -f Makefile.sim SIM=vivado compile

# Elaborate design
make -f Makefile.sim SIM=vivado elaborate

# Run simulation
make -f Makefile.sim SIM=vivado run

# Interactive GUI
make -f Makefile.sim SIM=vivado gui

# Cleanup
make -f Makefile.sim clean
```

**Generated files**: `work/`, `xsim.dir/`, `vivado_simulation.log`

---

## Shell Script Approach

For bash-based workflows, use the provided scripts in `scripts/`:

### VCS

```bash
./scripts/run_vcs.sh simple_dut.v generated_tb tb 1 0
#                    DUT             TESTBENCH    TOP SEED GUI
```

### Modelsim

```bash
./scripts/run_modelsim.sh simple_dut.v generated_tb tb 42 0
```

With GUI:
```bash
./scripts/run_modelsim.sh simple_dut.v generated_tb tb 1 1
```

### Xcelium

```bash
./scripts/run_xcelium.sh simple_dut.v generated_tb tb 123 0
```

### Vivado

```bash
./scripts/run_vivado.sh simple_dut.v generated_tb tb 1 0
```

---

## Complete Workflow Example

### 1. Generate Testbench

```bash
# Generate complete testbench with all components
py -m uvm_tbgen generate --dut examples/simple_dut.v \
                        --outdir gen_full \
                        --topname my_tb
```

### 2. Run with Different Simulators

```bash
# VCS
python3 run_simulation.py --simulator vcs \
                          --dut examples/simple_dut.v \
                          --testbench gen_full \
                          --seed 42

# Modelsim with GUI
python3 run_simulation.py --simulator modelsim \
                          --dut examples/simple_dut.v \
                          --testbench gen_full \
                          --gui

# Xcelium
python3 run_simulation.py --simulator xcelium \
                          --dut examples/simple_dut.v \
                          --testbench gen_full \
                          --seed 42

# Vivado
python3 run_simulation.py --simulator vivado \
                          --dut examples/simple_dut.v \
                          --testbench gen_full
```

### 3. View Results

All simulators generate log files:
- **VCS**: `vcs_simulation.log`
- **Modelsim**: `modelsim_simulation.log`
- **Xcelium**: `xcelium_simulation.log`
- **Vivado**: `vivado_simulation.log`

```bash
# View simulation output
tail -f vcs_simulation.log

# Search for errors
grep -i "error\|fail\|assert" xcelium_simulation.log
```

---

## Simulator Capabilities & Differences

### VCS (Synopsys)
- **Best for**: Large designs, high performance
- **Advantages**: Fastest compilation, robust assertion support
- **Compilation**: Generates `simv` executable
- **GUI**: Interactive waveform viewer
- **License**: Typically available in corporate environments

```bash
# VCS-specific options
vcs -full64 -sverilog -assert svaext +v2k -timescale=1ns/1ps
./simv +UVM_VERBOSITY=UVM_HIGH -gui -l output.log
```

### Modelsim (Mentor)
- **Best for**: Learning, prototyping
- **Advantages**: User-friendly, easy installation
- **Compilation**: Creates `work/` library
- **GUI**: Wave viewer integrated
- **License**: Often available for academic use

```bash
# Modelsim-specific
vlog -sv -work work *.sv
vsim -work work tb +UVM_VERBOSITY=UVM_HIGH -gui
```

### Xcelium (Cadence)
- **Best for**: Enterprise, SystemVerilog compliance
- **Advantages**: Single-pass compilation, excellent performance
- **Compilation**: One-step compilation and elaboration
- **GUI**: Verdi integrated
- **License**: Premium commercial tool

```bash
# Xcelium single-step
xrun -elaborate -sv -top tb *.sv -gui
```

### Vivado Simulator (Xilinx)
- **Best for**: FPGA-focused projects
- **Advantages**: FPGA design integration
- **Compilation**: Three steps (xvlog, xelab, xsim)
- **GUI**: Integrated with Vivado IDE
- **License**: Free with Vivado (WebPACK edition available)

```bash
# Vivado three-step
xvlog -sv *.sv
xelab tb
xsim tb -gui
```

---

## Troubleshooting

### Simulator Not Found

```bash
# Check if simulator is in PATH
which vcs
which vlog
which xrun
which xvlog

# If not found, add to PATH (example for VCS):
export PATH="/tools/synopsys/vcs-mx/bin:$PATH"
```

### Compilation Errors

1. Check SystemVerilog syntax:
   ```bash
   python3 run_simulation.py --list  # Verify tools installed
   ```

2. Check source file paths in testbench directory

3. Verify generated files exist:
   ```bash
   ls -la gen_full/*.sv
   ```

### Simulation Crashes

- Enable verbose output: `+UVM_VERBOSITY=UVM_DEBUG`
- Check log files for detailed error messages
- Try with different random seed: `--seed <value>`

### GUI Not Launching

- Ensure X11 forwarding if over SSH
- Check DISPLAY environment variable: `echo $DISPLAY`
- Some remote environments don't support GUI

---

## Performance Tips

### VCS
```bash
# Parallel compilation
vcs -j 8 *.sv  # 8 parallel jobs

# Optimized runtime
./simv +nowarn
```

### Modelsim
```bash
# Fast compilation mode
vlog -fast *.sv

# Optimized simulation
vsim -do "run -all" -c
```

### Xcelium
```bash
# Xcelium auto-parallelizes
xrun -elaborate -sv *.sv  # Uses all available cores

# Advanced coverage
xrun -coverage all *.sv
```

### Vivado
```bash
# Use Vivado batch mode for scripts
vivado -mode batch -source sim_script.tcl
```

---

## Code Generation Options by Simulator

All generated code uses **IEEE SystemVerilog-2017** standard features supported by all simulators:
- ✅ UVM 1.2 standard
- ✅ SystemVerilog assertions (SVA)
- ✅ Randomization (`rand`, `constraint`)
- ✅ Functional coverage (covergroups)
- ✅ Verification checkers

No simulator-specific constructs are used, ensuring portability across all tools.

---

## Continuous Integration

Run simulations in CI/CD pipelines:

```bash
#!/bin/bash
# ci_run_tests.sh

for SIM in vcs modelsim xcelium; do
  echo "Testing with $SIM..."
  python3 run_simulation.py --simulator $SIM \
                            --dut dut.v \
                            --testbench tb \
                            --seed $RANDOM
  if [ $? -ne 0 ]; then
    echo "FAILED: $SIM"
    exit 1
  fi
done

echo "All simulators passed!"
```

---

## Additional Resources

- **VCS Documentation**: https://www.synopsys.com/tools/verification/vcs.html
- **Modelsim User Guide**: https://www.mentor.com/products/fv/modelsim/
- **Xcelium**: https://www.cadence.com/en_US/home/tools/system-design-and-verification/simulation-and-testbench-automation/xcelium-parallel-simulator.html
- **Vivado Simulator**: https://www.xilinx.com/products/design-tools/vivado/vivado-ml-edition.html
- **UVM Standard**: https://accellera.org/activities/standards/systemverilog/
- **SystemVerilog LRM**: https://standards.ieee.org/standard/1800-2017.html
