#!/usr/bin/env python3
"""
Universal Simulator Runner for UVM Testbenches
Supports: VCS, Modelsim, Xcelium, Vivado Simulator
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict

class SimulatorConfig:
    """Simulator configuration and detection"""
    
    SIMULATORS = {
        'vcs': {
            'name': 'VCS (Synopsys)',
            'commands': ['vcs', 'vlogan'],
            'compile_cmd': 'vcs',
            'run_cmd': './simv',
            'elaboration_flag': '-elaborate',
            'top_flag': '-top',
            'source_flag': None,  # Sources listed as arguments
        },
        'modelsim': {
            'name': 'Modelsim (Mentor)',
            'commands': ['vlog', 'vsim', 'vcom'],
            'compile_cmd': 'vlog',
            'run_cmd': 'vsim',
            'elaboration_flag': None,
            'top_flag': None,
            'source_flag': None,
        },
        'xcelium': {
            'name': 'Xcelium (Cadence)',
            'commands': ['xrun', 'xvlog'],
            'compile_cmd': 'xrun',
            'run_cmd': 'xrun',
            'elaboration_flag': None,
            'top_flag': '-top',
            'source_flag': '-sv',
        },
        'vivado': {
            'name': 'Vivado Simulator (Xilinx)',
            'commands': ['xvlog', 'xsim', 'vivado'],
            'compile_cmd': 'xvlog',
            'run_cmd': 'xsim',
            'elaboration_flag': None,
            'top_flag': None,
            'source_flag': '-sv',
        },
    }

    @classmethod
    def detect_available_simulators(cls) -> List[str]:
        """Detect which simulators are installed"""
        available = []
        for sim_name, config in cls.SIMULATORS.items():
            for cmd in config['commands']:
                try:
                    result = subprocess.run(['which', cmd], capture_output=True, timeout=5)
                    if result.returncode == 0:
                        available.append(sim_name)
                        break
                except Exception:
                    pass
        return available

    @classmethod
    def get_simulator_config(cls, simulator: str) -> Dict:
        """Get configuration for a specific simulator"""
        return cls.SIMULATORS.get(simulator.lower())


class TestbenchSimulator:
    """Run UVM testbenches with different simulators"""

    def __init__(self, simulator: str, dut_path: str, testbench_dir: str, top_module: str = 'tb'):
        self.simulator = simulator.lower()
        self.config = SimulatorConfig.get_simulator_config(self.simulator)
        if not self.config:
            raise ValueError(f"Unknown simulator: {simulator}")
        
        self.dut_path = Path(dut_path)
        self.testbench_dir = Path(testbench_dir)
        self.top_module = top_module
        self.work_dir = self.testbench_dir / 'work'
        self.log_file = self.testbench_dir / f'{self.simulator}_simulation.log'

    def prepare(self):
        """Prepare for simulation"""
        self.work_dir.mkdir(exist_ok=True)
        print(f"[{self.simulator.upper()}] Simulator Configuration:")
        print(f"  DUT: {self.dut_path}")
        print(f"  Testbench: {self.testbench_dir}")
        print(f"  Work Directory: {self.work_dir}")

    def collect_sources(self) -> List[str]:
        """Collect all SystemVerilog source files"""
        sources = []
        
        # Add DUT
        sources.append(str(self.dut_path))
        
        # Add generated testbench files
        for sv_file in sorted(self.testbench_dir.glob('*.sv')):
            sources.append(str(sv_file))
        
        return sources

    def run_vcs(self, sources: List[str], gui: bool = False, seed: Optional[int] = None) -> int:
        """Run simulation with VCS"""
        print(f"\n[VCS] Compiling and elaborating design...")
        
        cmd = [
            'vcs',
            '-full64',
            '-sverilog',
            '-assert', 'svaext',
            '-timescale=1ns/1ps',
            '+v2k',
            '-top', self.top_module,
        ]
        
        if gui:
            cmd.append('-gui')
        
        if seed:
            cmd.extend(['+ntb_random_seed', str(seed)])
        
        cmd.extend(sources)
        
        print(f"Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=self.testbench_dir, capture_output=False)
        
        if result.returncode == 0:
            print(f"\n[VCS] Running simulation...")
            run_cmd = ['./simv', f'-l', str(self.log_file)]
            if gui:
                run_cmd.append('-gui')
            result = subprocess.run(run_cmd, cwd=self.testbench_dir)
        
        return result.returncode

    def run_modelsim(self, sources: List[str], gui: bool = False, seed: Optional[int] = None) -> int:
        """Run simulation with Modelsim"""
        print(f"\n[MODELSIM] Compiling design...")
        
        # Create modelsim.ini if needed
        modelsim_ini = self.work_dir / 'modelsim.ini'
        if not modelsim_ini.exists():
            subprocess.run(['vlib', str(self.work_dir)], cwd=self.testbench_dir)
        
        # Compile SystemVerilog files
        cmd = ['vlog', '-sv', '-work', str(self.work_dir)]
        cmd.extend(sources)
        
        print(f"Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=self.testbench_dir, capture_output=False)
        
        if result.returncode == 0:
            print(f"\n[MODELSIM] Running simulation...")
            run_cmd = ['vsim', '-work', str(self.work_dir), self.top_module]
            
            if gui:
                run_cmd.append('-gui')
            
            if seed:
                run_cmd.extend(['-sv_seed', str(seed)])
            
            run_cmd.extend(['-l', str(self.log_file)])
            
            result = subprocess.run(run_cmd, cwd=self.testbench_dir)
        
        return result.returncode

    def run_xcelium(self, sources: List[str], gui: bool = False, seed: Optional[int] = None) -> int:
        """Run simulation with Xcelium"""
        print(f"\n[XCELIUM] Compiling and running design...")
        
        cmd = [
            'xrun',
            '-elaborate',
            '-64bit',
            '-sv',
            '-top', self.top_module,
            '-timescale', '1ns/1ps',
        ]
        
        if gui:
            cmd.append('-gui')
        
        if seed:
            cmd.extend(['-random_seed', str(seed)])
        
        cmd.extend(['-l', str(self.log_file)])
        cmd.extend(sources)
        
        print(f"Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=self.testbench_dir, capture_output=False)
        
        return result.returncode

    def run_vivado(self, sources: List[str], gui: bool = False, seed: Optional[int] = None) -> int:
        """Run simulation with Vivado Simulator"""
        print(f"\n[VIVADO] Compiling design...")
        
        # Compile with xvlog
        compile_cmd = ['xvlog', '-sv', '--work', str(self.work_dir)]
        compile_cmd.extend(sources)
        
        print(f"Command: {' '.join(compile_cmd)}")
        result = subprocess.run(compile_cmd, cwd=self.testbench_dir, capture_output=False)
        
        if result.returncode == 0:
            print(f"\n[VIVADO] Elaborating design...")
            elab_cmd = ['xelab', '--work', str(self.work_dir), self.top_module]
            result = subprocess.run(elab_cmd, cwd=self.testbench_dir, capture_output=False)
        
        if result.returncode == 0:
            print(f"\n[VIVADO] Running simulation...")
            run_cmd = ['xsim', f'{self.work_dir}/{self.top_module}']
            
            if gui:
                run_cmd.append('-gui')
            
            run_cmd.extend(['-l', str(self.log_file)])
            
            result = subprocess.run(run_cmd, cwd=self.testbench_dir)
        
        return result.returncode

    def run(self, gui: bool = False, seed: Optional[int] = None) -> int:
        """Run simulation with appropriate simulator"""
        self.prepare()
        sources = self.collect_sources()
        
        print(f"\n[INFO] Using {self.config['name']}")
        print(f"[INFO] Sources found: {len(sources)}")
        
        try:
            if self.simulator == 'vcs':
                return self.run_vcs(sources, gui, seed)
            elif self.simulator == 'modelsim':
                return self.run_modelsim(sources, gui, seed)
            elif self.simulator == 'xcelium':
                return self.run_xcelium(sources, gui, seed)
            elif self.simulator == 'vivado':
                return self.run_vivado(sources, gui, seed)
        except KeyboardInterrupt:
            print(f"\n[INTERRUPTED] Simulation cancelled by user")
            return 1
        except Exception as e:
            print(f"[ERROR] Simulation failed: {e}")
            return 1


def main():
    parser = argparse.ArgumentParser(
        description='Run UVM testbenches with multiple industry simulators',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with VCS
  python3 run_simulation.py --simulator vcs --dut dut.v --testbench gen_tb

  # Run with Modelsim in GUI mode
  python3 run_simulation.py --simulator modelsim --dut dut.v --testbench gen_tb --gui

  # Run with Xcelium with specific seed
  python3 run_simulation.py --simulator xcelium --dut dut.v --testbench gen_tb --seed 12345

  # Auto-detect and run with first available simulator
  python3 run_simulation.py --dut dut.v --testbench gen_tb --auto
        """
    )
    
    parser.add_argument('--simulator', type=str, help='Simulator to use (vcs, modelsim, xcelium, vivado)')
    parser.add_argument('--dut', type=str, help='Path to DUT file')
    parser.add_argument('--testbench', type=str, help='Path to testbench directory')
    parser.add_argument('--top', default='tb', type=str, help='Top module name (default: tb)')
    parser.add_argument('--gui', action='store_true', help='Launch simulation in GUI mode')
    parser.add_argument('--seed', type=int, help='Random seed for simulation')
    parser.add_argument('--list', action='store_true', help='List available simulators')
    parser.add_argument('--auto', action='store_true', help='Auto-detect and use first available simulator')
    
    args = parser.parse_args()
    
    if args.list:
        available = SimulatorConfig.detect_available_simulators()
        print("Available simulators:")
        if available:
            for sim in available:
                config = SimulatorConfig.get_simulator_config(sim)
                print(f"  ✓ {config['name']}")
        else:
            print("  No simulators found. Please install one of:")
            for sim_name, config in SimulatorConfig.SIMULATORS.items():
                print(f"    - {config['name']}")
        return 0
    
    # Make dut and testbench required only if not using --list
    if not args.dut or not args.testbench:
        if not args.list and not args.auto:
            parser.error("--dut and --testbench are required (or use --list or --auto)")
        # If using --auto, we still need these
        if args.auto and (not args.dut or not args.testbench):
            parser.error("--dut and --testbench are required with --auto")
    
    if args.auto:
        available = SimulatorConfig.detect_available_simulators()
        if not available:
            print("[ERROR] No simulators found. Install VCS, Modelsim, Xcelium, or Vivado Simulator.")
            return 1
        simulator = available[0]
        print(f"[INFO] Auto-detected simulator: {SimulatorConfig.get_simulator_config(simulator)['name']}")
    else:
        if not args.simulator:
            print("[ERROR] Specify --simulator or use --auto")
            return 1
        simulator = args.simulator
    
    try:
        runner = TestbenchSimulator(simulator, args.dut, args.testbench, args.top)
        return runner.run(args.gui, args.seed)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return 1
    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
