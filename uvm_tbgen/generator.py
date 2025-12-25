from pathlib import Path
import re
import shutil
from typing import List, NamedTuple
from jinja2 import Environment, FileSystemLoader, Template


class Port(NamedTuple):
    """Represents a Verilog port with direction, width, and name."""
    name: str
    direction: str = "input"  # "input", "output", "inout"
    width: int = 1

    def signal_decl(self) -> str:
        """Return the signal declaration for testbench."""
        if self.width == 1:
            return f"logic {self.name};"
        return f"logic [{self.width - 1}:0] {self.name};"

    def connection(self) -> str:
        """Return the DUT instantiation connection."""
        return f".{self.name}({self.name})"


def _extract_module_and_ports(verilog_text: str):
    """Return (module_name, [Port]) using a heuristic parser.

    This handles common styles where the module header lists ports and
    where ports are later declared with `input|output|inout`.
    """
    m = re.search(
        r"module\s+([a-zA-Z_]\w*)\s*\((.*?)\)\s*;", verilog_text, re.S
    )
    if not m:
        raise ValueError("No module header found")
    module_name = m.group(1)
    header = m.group(2)

    # Try to extract port declarations from header
    parts = [p.strip() for p in header.split(",") if p.strip()]
    ports: List[Port] = []
    
    for part in parts:
        # Extract direction, width, and name from e.g. "input [7:0] data"
        dir_match = re.match(r"(\w+)\s*(?:\[(\d+):(\d+)\])?\s*([a-zA-Z_]\w*)", part)
        if dir_match:
            direction = dir_match.group(1) if dir_match.group(1) in [
                "input", "output", "inout"
            ] else "input"
            msb = int(dir_match.group(2)) if dir_match.group(2) else 0
            lsb = int(dir_match.group(3)) if dir_match.group(3) else 0
            width = abs(msb - lsb) + 1
            name = dir_match.group(4)
            ports.append(Port(name, direction, width))

    # Also search for declared ports inside the module body: e.g. input [7:0] bus;
    body = verilog_text[m.end():]
    decl_pattern = r"(input|output|inout)\s*(?:\[(\d+):(\d+)\])?\s*([a-zA-Z_]\w*)"
    for match in re.finditer(decl_pattern, body):
        direction = match.group(1)
        msb = int(match.group(2)) if match.group(2) else 0
        lsb = int(match.group(3)) if match.group(3) else 0
        width = abs(msb - lsb) + 1
        name = match.group(4)
        # Avoid duplicates
        if not any(p.name == name for p in ports):
            ports.append(Port(name, direction, width))

    return module_name, ports


class TBGenerator:
    def __init__(self, dut_path: str, outdir: str, topname: str):
        self.dut_path = dut_path
        self.outdir = outdir
        self.topname = topname
        self.template_dir = Path(__file__).parent.parent / "templates"

    def generate(self) -> None:
        """Generate complete UVM testbench with components using Jinja2 templates.

        Generates:
        - seq_item.sv: Transaction class
        - driver.sv: Driver component
        - monitor.sv: Monitor component
        - sequencer.sv: Sequencer and base sequence
        - agent.sv: Agent grouping driver, sequencer, monitor
        - scoreboard.sv: Scoreboard component
        - env.sv: Environment
        - test.sv: Base test
        - interface.sv: DUT interface
        - tb_top.sv: Top module connecting all
        """
        print(f"[uvm_tbgen] Generating testbench for {self.dut_path}")
        print(f"[uvm_tbgen] Output dir: {self.outdir}, top: {self.topname}")

        outdir = Path(self.outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        # Copy the DUT file into the output directory
        dut_src = Path(self.dut_path)
        if not dut_src.exists():
            raise FileNotFoundError(f"DUT not found: {self.dut_path}")
        dut_dst = outdir / dut_src.name
        shutil.copy2(dut_src, dut_dst)

        verilog_text = dut_dst.read_text(encoding="utf-8")
        try:
            module_name, ports = _extract_module_and_ports(verilog_text)
        except ValueError:
            module_name = dut_dst.stem
            ports = []

        # Separate ports by direction
        input_ports = [p for p in ports if p.direction == "input"]
        output_ports = [p for p in ports if p.direction == "output"]
        inout_ports = [p for p in ports if p.direction == "inout"]

        # Analyze ports for assertion patterns
        assertion_context = self._analyze_ports_for_assertions(
            module_name, ports, input_ports, output_ports
        )

        # Setup Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        context = {
            "module": module_name,
            "topname": self.topname,
            "ports": ports,
            "all_ports": ports,  # Add all_ports to context
            "input_ports": input_ports,
            "output_ports": output_ports,
            "inout_ports": inout_ports,
            **assertion_context,  # Add assertion-specific context
        }

        # Generate each component
        components = [
            ("seq_item.sv.j2", f"{module_name}_seq_item.sv"),
            ("driver.sv.j2", f"{module_name}_driver.sv"),
            ("monitor.sv.j2", f"{module_name}_monitor.sv"),
            ("sequencer.sv.j2", f"{module_name}_sequencer.sv"),
            ("agent.sv.j2", f"{module_name}_agent.sv"),
            ("scoreboard.sv.j2", f"{module_name}_scoreboard.sv"),
            ("env_generated.sv.j2", f"{module_name}_env.sv"),
            ("test.sv.j2", f"{module_name}_test.sv"),
            ("coverage.sv.j2", f"{module_name}_coverage.sv"),
            ("checker.sv.j2", f"{module_name}_checker.sv"),
        ]

        for template_file, output_file in components:
            try:
                template = env.get_template(template_file)
                content = template.render(context)
                output_path = outdir / output_file
                output_path.write_text(content, encoding="utf-8")
                print(f"[uvm_tbgen] Generated {output_file}")
            except Exception as e:
                print(f"[uvm_tbgen] Warning: Failed to generate {template_file}: {e}")

        # Generate assertions
        try:
            template = env.get_template("assertions.sv.j2")
            content = template.render(context)
            output_path = outdir / f"{module_name}_assertions.sv"
            output_path.write_text(content, encoding="utf-8")
            print(f"[uvm_tbgen] Generated {module_name}_assertions.sv")
        except Exception as e:
            print(f"[uvm_tbgen] Warning: Failed to generate assertions: {e}")

        # Generate interface
        try:
            template = env.get_template("interface.sv.j2")
            # Map Port to template format
            ports_for_if = [
                {
                    "name": p.name,
                    "dir": p.direction,
                    "width": f"[{p.width - 1}:0]" if p.width > 1 else "",
                }
                for p in ports
            ]
            context["ports"] = ports_for_if
            content = template.render(context)
            output_path = outdir / f"{module_name}_if.sv"
            output_path.write_text(content, encoding="utf-8")
            print(f"[uvm_tbgen] Generated {module_name}_if.sv")
        except Exception as e:
            print(f"[uvm_tbgen] Warning: Failed to generate interface: {e}")

        # Generate top module using tb_top.sv.j2 if it exists
        try:
            template = env.get_template("tb_top.sv.j2")
            context["ports"] = ports
            content = template.render(context)
            output_path = outdir / f"{self.topname}.sv"
            output_path.write_text(content, encoding="utf-8")
            print(f"[uvm_tbgen] Generated {self.topname}.sv")
        except Exception as e:
            print(f"[uvm_tbgen] tb_top.sv.j2 not found or error; using fallback top module")
            self._generate_fallback_top(outdir, module_name, ports)

        print(f"[uvm_tbgen] Testbench generation complete!")

    def _generate_fallback_top(
        self, outdir: Path, module_name: str, ports: List[Port]
    ) -> None:
        """Generate a simple fallback top module if tb_top.sv.j2 not available."""
        content = (
            f"// Auto-generated UVM testbench top (fallback)\n"
            f"`timescale 1ns/1ps\n"
            f"`include \"uvm_macros.svh\"\n"
            f"import uvm_pkg::*;\n\n"
            f"module {self.topname};\n\n"
            f"  // DUT interface\n"
            f"  {module_name}_if dut_if();\n\n"
            f"  // DUT instance\n"
            f"  {module_name} dut_inst (\n"
        )

        for i, p in enumerate(ports):
            comma = "," if i < len(ports) - 1 else ""
            content += f"    .{p.name}(dut_if.{p.name}){comma}\n"

        content += (
            f"  );\n\n"
            f"  initial begin\n"
            f"    run_test();\n"
            f"  end\n"
            f"endmodule\n"
        )

        output_path = outdir / f"{self.topname}.sv"
        output_path.write_text(content, encoding="utf-8")
        print(f"[uvm_tbgen] Generated {self.topname}.sv (fallback)")

    def _generate_uvm_scaffold(self, module_name: str, ports: List[Port]) -> str:
        """Legacy scaffold generator (retained for reference; replaced by Jinja2 templates)."""
        return ""

    def _analyze_ports_for_assertions(
        self, module_name: str, all_ports: List[Port], input_ports: List[Port],
        output_ports: List[Port]
    ) -> dict:
        """Analyze ports to generate meaningful SVA properties and constraints."""
        context = {
            "reset_port": None,
            "has_valid_signal": False,
            "has_ready_signal": False,
            "multiple_control_signals": False,
            "control_signals": [],
        }

        # Find reset signal
        reset_candidates = [
            p for p in input_ports
            if "rst" in p.name.lower() or "reset" in p.name.lower()
        ]
        if reset_candidates:
            context["reset_port"] = reset_candidates[0].name

        # Find valid/ready handshake signals
        for p in output_ports:
            if "valid" in p.name.lower():
                context["has_valid_signal"] = True

        for p in input_ports:
            if "ready" in p.name.lower():
                context["has_ready_signal"] = True

        # Find control signals (enable, write, read, etc.)
        control_keywords = ["enable", "en", "write", "read", "wr", "rd"]
        for p in input_ports:
            name_lower = p.name.lower()
            if any(kw in name_lower for kw in control_keywords):
                context["control_signals"].append(p.name)

        if len(context["control_signals"]) > 1:
            context["multiple_control_signals"] = True

        return context

