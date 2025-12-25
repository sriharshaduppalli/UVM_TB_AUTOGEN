import os
from jinja2 import Environment, FileSystemLoader
from .uvm_tbgen.uvm_tbgen.parser import parse_dut

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

class TBGenerator:
    def __init__(self, dut_path, outdir='generated_tb', topname=None, mapping=None):
        self.dut_path = dut_path
        self.outdir = outdir
        self.mapping = mapping or {}
        self.env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), trim_blocks=True, lstrip_blocks=True)
        self.parsed = parse_dut(dut_path)
        self.topname = topname or f"{self.parsed['module']}_tb"
        os.makedirs(self.outdir, exist_ok=True)

    def render(self, template_name, context, outname):
        tpl = self.env.get_template(template_name)
        content = tpl.render(**context)
        with open(os.path.join(self.outdir, outname), 'w') as f:
            f.write(content)
        print(f"Generated {outname}")

    def generate_interface(self):
        # default: create a simple interface mapping for grouped ports
        context = {'module': self.parsed['module'], 'ports': self.parsed['ports']}
        self.render('interface.sv.j2', context, f"{self.parsed['module']}_if.sv")

    def generate_env(self):
        context = {'module': self.parsed['module'], 'ports': self.parsed['ports'], 'topname': self.topname}
        self.render('env.sv.j2', context, 'env.sv')
        self.render('agent.sv.j2', context, 'agent.sv')
        self.render('driver.sv.j2', context, 'driver.sv')
        self.render('monitor.sv.j2', context, 'monitor.sv')
        self.render('seq_item.sv.j2', context, 'seq_item.sv')
        self.render('sequence.sv.j2', context, 'sequence.sv')
        self.render('scoreboard.sv.j2', context, 'scoreboard.sv')
        self.render('test.sv.j2', context, 'test.sv')

    def generate_tb_top(self):
        context = {'module': self.parsed['module'], 'ports': self.parsed['ports'], 'topname': self.topname}
        self.render('tb_top.sv.j2', context, f"{self.topname}.sv")

    def generate(self):
        # copy DUT
        dut_dst = os.path.join(self.outdir, os.path.basename(self.dut_path))
        with open(self.dut_path, 'r', errors='ignore') as src, open(dut_dst, 'w') as dst:
            dst.write(src.read())
        print(f"Copied DUT to {dut_dst}")
        # generate components
        self.generate_interface()
        self.generate_env()
        self.generate_tb_top()
        # create a simple run script
        run_sh = f"""#!/bin/bash
# Simple run script for Xcelium or other simulator
# Adjust compile and run commands as needed
iverilog -g2012 -o simv {os.path.basename(self.dut_path)} *.sv
vvp simv
"""
        with open(os.path.join(self.outdir, 'run.sh'), 'w') as f:
            f.write(run_sh)
        os.chmod(os.path.join(self.outdir, 'run.sh'), 0o755)
        print("Generated run.sh")