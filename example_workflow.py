#!/usr/bin/env python3
"""
Complete Example: Generate and Run Testbenches on Multiple Simulators
This script demonstrates the full workflow of generating a testbench and
running it with different industry simulators.
"""

import subprocess
import sys
from pathlib import Path

def print_header(title):
    """Print formatted section header"""
    width = 70
    print("\n" + "=" * width)
    print(f"  {title}".ljust(width - 1) + "=")
    print("=" * width)

def run_command(cmd, description=""):
    """Run a command and report status"""
    if description:
        print(f"\n[*] {description}")
    print(f"    Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    
    try:
        if isinstance(cmd, list):
            result = subprocess.run(cmd, capture_output=False, timeout=60)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=False, timeout=60)
        
        if result.returncode == 0:
            print(f"    ✓ Success")
            return True
        else:
            print(f"    ✗ Failed (exit code: {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print(f"    ✗ Timeout")
        return False
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def main():
    print_header("UVM Testbench Generator - Complete Example")
    
    # Configuration
    DUT = "examples/simple_dut.v"
    TESTBENCH_DIR = "example_tb"
    TOP_MODULE = "simple_tb"
    
    print(f"\nConfiguration:")
    print(f"  DUT: {DUT}")
    print(f"  Output Directory: {TESTBENCH_DIR}")
    print(f"  Top Module: {TOP_MODULE}")
    
    # Step 1: Generate testbench
    print_header("Step 1: Generate Testbench")
    
    generate_cmd = [
        "py", "-m", "uvm_tbgen", "generate",
        "--dut", DUT,
        "--outdir", TESTBENCH_DIR,
        "--topname", TOP_MODULE
    ]
    
    if not run_command(generate_cmd, "Generating testbench components"):
        print("[ERROR] Testbench generation failed!")
        sys.exit(1)
    
    # Verify generation
    tb_dir = Path(TESTBENCH_DIR)
    expected_files = [
        "simple_dut_seq_item.sv",
        "simple_dut_driver.sv",
        "simple_dut_monitor.sv",
        "simple_dut_sequencer.sv",
        "simple_dut_agent.sv",
        "simple_dut_scoreboard.sv",
        "simple_dut_env.sv",
        "simple_dut_test.sv",
        "simple_dut_assertions.sv",
        "simple_dut_coverage.sv",
        "simple_dut_checker.sv",
        "simple_dut_if.sv",
        "simple_tb.sv"
    ]
    
    print("\n[*] Verifying generated files...")
    all_found = True
    for file in expected_files:
        file_path = tb_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"    ✓ {file:30} ({size:5} bytes)")
        else:
            print(f"    ✗ {file:30} NOT FOUND")
            all_found = False
    
    if not all_found:
        print("[ERROR] Some generated files are missing!")
        sys.exit(1)
    
    # Step 2: Check available simulators
    print_header("Step 2: Detect Available Simulators")
    
    check_simulators = [
        "py", "run_simulation.py", "--list"
    ]
    
    run_command(check_simulators, "Checking for installed simulators")
    
    # Step 3: Example simulation commands (informational)
    print_header("Step 3: Simulator Usage Examples")
    
    print("\nThe generated testbench can be run with any of the following commands:")
    
    simulators = {
        "VCS (Synopsys)": "py run_simulation.py --simulator vcs --dut {} --testbench {} --seed 42",
        "Modelsim (Mentor)": "py run_simulation.py --simulator modelsim --dut {} --testbench {}",
        "Xcelium (Cadence)": "py run_simulation.py --simulator xcelium --dut {} --testbench {} --gui",
        "Vivado (Xilinx)": "py run_simulation.py --simulator vivado --dut {} --testbench {}",
    }
    
    for sim_name, cmd_template in simulators.items():
        cmd = cmd_template.format(DUT, TESTBENCH_DIR)
        print(f"\n{sim_name}:")
        print(f"  {cmd}")
    
    # Step 4: Test parsing with Python UVM generator
    print_header("Step 4: Testbench Statistics")
    
    total_lines = 0
    total_files = 0
    
    for sv_file in sorted(tb_dir.glob("*.sv")):
        with open(sv_file, 'r') as f:
            lines = len(f.readlines())
            total_lines += lines
            total_files += 1
    
    print(f"\nGenerated Testbench Summary:")
    print(f"  Total Files: {total_files}")
    print(f"  Total Lines of Code: {total_lines}")
    print(f"  Average File Size: {total_lines // total_files if total_files > 0 else 0} lines")
    
    # File breakdown
    print(f"\nFile Breakdown:")
    file_info = []
    for sv_file in sorted(tb_dir.glob("*.sv")):
        with open(sv_file, 'r') as f:
            lines = len(f.readlines())
            file_info.append((sv_file.name, lines))
    
    for filename, lines in sorted(file_info, key=lambda x: x[1], reverse=True):
        component_type = "UVM Component"
        if "seq_item" in filename:
            component_type = "Transaction"
        elif "driver" in filename:
            component_type = "Driver"
        elif "monitor" in filename:
            component_type = "Monitor"
        elif "sequencer" in filename:
            component_type = "Sequencer"
        elif "agent" in filename:
            component_type = "Agent"
        elif "scoreboard" in filename:
            component_type = "Scoreboard"
        elif "env" in filename:
            component_type = "Environment"
        elif "test" in filename:
            component_type = "Test"
        elif "assertions" in filename:
            component_type = "Assertions"
        elif "coverage" in filename:
            component_type = "Coverage"
        elif "checker" in filename:
            component_type = "Checker"
        elif "if" in filename:
            component_type = "Interface"
        else:
            component_type = "Top Module"
        
        print(f"  {filename:30} {lines:4} lines  ({component_type})")
    
    # Step 5: Next steps
    print_header("Step 5: Next Steps")
    
    print("""
To run simulations:

1. If you have VCS installed:
   py run_simulation.py --simulator vcs --dut {} --testbench {} --seed 42

2. If you have Modelsim installed:
   py run_simulation.py --simulator modelsim --dut {} --testbench {}

3. Or auto-detect available simulator:
   py run_simulation.py --dut {} --testbench {} --auto

To view generated files:
   ls -la {}

To inspect specific component:
   cat {}/simple_dut_assertions.sv     # View assertions
   cat {}/simple_dut_coverage.sv       # View coverage model
   cat {}/simple_dut_checker.sv        # View behavioral checker

For detailed simulator guide:
   cat SIMULATOR_GUIDE.md

For simulator comparison:
   cat SIMULATOR_MATRIX.md
    """.format(DUT, TESTBENCH_DIR, DUT, TESTBENCH_DIR, 
               DUT, TESTBENCH_DIR, TESTBENCH_DIR, TESTBENCH_DIR, 
               TESTBENCH_DIR, TESTBENCH_DIR))
    
    print_header("Example Complete ✓")
    print("\nTestbench successfully generated and ready for simulation!")
    print(f"Location: {TESTBENCH_DIR}/")

if __name__ == "__main__":
    main()
