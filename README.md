# uvm-tbgen

A Python tool to auto-generate complete SystemVerilog UVM testbench environments from Verilog DUT files.

## Features

- **Complete UVM Generation**: Automatically generates all UVM components (driver, monitor, sequencer, agent, scoreboard, environment, test).
- **Jinja2 Template Engine**: Uses Jinja2 templates for flexible, extensible component generation.
- **DUT Parsing**: Extracts module name and port information (direction, bit widths).
- **Port Classification**: Automatically separates input, output, and inout ports for proper component roles.
- **File Generation**: Creates all components including:
  - `seq_item.sv`: Transaction class with fields for all ports
  - `driver.sv`: Stimulus driver
  - `monitor.sv`: Passive monitor with TLM analysis port
  - `sequencer.sv`: Sequencer and base sequence
  - `agent.sv`: Agent grouping driver, sequencer, monitor
  - `scoreboard.sv`: Scoreboard with TLM FIFO
  - `env.sv`: Environment with agent and scoreboard
  - `test.sv`: Base test class
  - `interface.sv`: SystemVerilog interface for DUT
  - `{topname}.sv`: Top-level module
- **CLI Tool**: Easy-to-use command-line interface for quick testbench generation.

## Installation

Install the package in editable mode:

```bash
pip install -e .
```

This installs the `uvm-tbgen` command globally and includes Jinja2 dependency.

## Usage

### Command Line

Generate a complete UVM testbench from a DUT:

```bash
py -m uvm_tbgen generate --dut examples/simple_dut.v --outdir gen_uvm --topname simple_tb
```

**Options:**
- `--dut PATH`: Path to the Verilog DUT file (required).
- `--outdir DIR`: Output directory for generated files (default: `generated_tb`).
- `--topname NAME`: Name of the top-level testbench module (default: `my_dut_tb`).

## Running Simulations with Industry Simulators

The generated testbenches work with all industry-standard SystemVerilog simulators. See [SIMULATOR_GUIDE.md](SIMULATOR_GUIDE.md) for detailed instructions.

### Quick Simulator Verification

```bash
# List available simulators on your system
python3 run_simulation.py --list
```

### Run Simulations

**Auto-detect simulator:**
```bash
python3 run_simulation.py --dut examples/simple_dut.v \
                          --testbench gen_uvm \
                          --auto
```

**VCS (Synopsys):**
```bash
python3 run_simulation.py --simulator vcs \
                          --dut examples/simple_dut.v \
                          --testbench gen_uvm \
                          --seed 42
```

**Modelsim (Mentor):**
```bash
python3 run_simulation.py --simulator modelsim \
                          --dut examples/simple_dut.v \
                          --testbench gen_uvm \
                          --gui
```

**Xcelium (Cadence):**
```bash
python3 run_simulation.py --simulator xcelium \
                          --dut examples/simple_dut.v \
                          --testbench gen_uvm
```

**Vivado Simulator (Xilinx):**
```bash
python3 run_simulation.py --simulator vivado \
                          --dut examples/simple_dut.v \
                          --testbench gen_uvm
```

### Using Make for Simulation

Alternatively, use the provided Makefile for traditional workflows:

```bash
# Compile with VCS
make -f Makefile.sim SIM=vcs compile

# Run simulation
make -f Makefile.sim SIM=vcs run

# Launch GUI
make -f Makefile.sim SIM=modelsim gui

# Clean artifacts
make -f Makefile.sim clean
```

Supported simulators in Makefile:
- `SIM=vcs` - VCS (Synopsys)
- `SIM=modelsim` - Modelsim (Mentor)
- `SIM=xcelium` - Xcelium (Cadence)
- `SIM=vivado` - Vivado Simulator (Xilinx)

### Python API

Use the generator in your Python scripts:

```python
from uvm_tbgen.generator import TBGenerator

gen = TBGenerator(
    dut_path="examples/simple_dut.v",
    outdir="gen_uvm",
    topname="simple_tb"
)
gen.generate()
```

## Generated Output

Running the generator produces the following files in `{outdir}/`:

### UVM Components
- **`{module}_seq_item.sv`**: Transaction class with randomizable input ports and output ports
- **`{module}_driver.sv`**: UVM driver receiving transactions from sequencer
- **`{module}_monitor.sv`**: Passive monitor observing all input ports via TLM
- **`{module}_sequencer.sv`**: Sequencer and base sequence for stimulus generation
- **`{module}_agent.sv`**: UVM agent containing driver, sequencer, and monitor
- **`{module}_scoreboard.sv`**: Scoreboard with TLM FIFO for transaction collection
- **`{module}_env.sv`**: Environment with agent and scoreboard, proper TLM connections
- **`{module}_test.sv`**: Base test class extending uvm_test

### Support Files
- **`{module}_if.sv`**: SystemVerilog interface with signals for all DUT ports
- **`{topname}.sv`**: Top-level module instantiating DUT and interface
- **`{module}.v`**: Copied DUT file

## Example

Given this DUT:

```verilog
module simple_dut(
  input clk,
  input rst_n,
  input [7:0] in_data,
  output valid
);
  // DUT implementation
endmodule
```

Running:

```bash
py -m uvm_tbgen generate --dut simple_dut.v --outdir gen --topname my_tb
```

Generates:

### Generated Sequence Item (`simple_dut_seq_item.sv`):
```systemverilog
class simple_dut_seq_item extends uvm_sequence_item;
  `uvm_object_utils(simple_dut_seq_item)

  // Input ports (stimulus)
  rand logic clk;
  rand logic rst_n;
  rand logic [7:0] in_data;

  // Output ports (observation)
  logic valid;
  
  // ... do_copy, do_print ...
endclass
```

### Generated Driver (`simple_dut_driver.sv`):
```systemverilog
class simple_dut_driver extends uvm_driver;
  `uvm_component_utils(simple_dut_driver)

  virtual simple_dut_if vif;
  simple_dut_seq_item item;

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    if (!uvm_config_db#(virtual simple_dut_if)::get(this, "", "vif", vif))
      `uvm_fatal("NOVIF", "Virtual interface not found")
  endfunction

  task run_phase(uvm_phase phase);
    forever begin
      @(posedge vif.clk);
      $display("[simple_dut_driver] Driving stimulus");
    end
  endtask
endclass
```

### Generated Environment (`simple_dut_env.sv`):
```systemverilog
class simple_dut_env extends uvm_env;
  `uvm_component_utils(simple_dut_env)

  simple_dut_agent agt;
  simple_dut_scoreboard sb;

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    agt = simple_dut_agent::type_id::create("agt", this);
    sb = simple_dut_scoreboard::type_id::create("sb", this);
  endfunction

  function void connect_phase(uvm_phase phase);
    super.connect_phase(phase);
    agt.mon.ap.connect(sb.mon_export);
  endfunction
endclass
```

## Architecture

### Components

- **`uvm_tbgen/generator.py`**: Core generator and parser.
  - `Port`: NamedTuple for port metadata (name, direction, width).
  - `_extract_module_and_ports()`: Heuristic parser for Verilog modules.
  - `TBGenerator`: Main class using Jinja2 to render templates.

- **`uvm_tbgen/cli.py`**: Command-line interface using `argparse`.

- **`uvm_tbgen/__main__.py`**: Entry point for `python -m uvm_tbgen`.

### Templates

Located in `templates/` directory:

- **`seq_item.sv.j2`**: Transaction class with port fields
- **`driver.sv.j2`**: UVM driver
- **`monitor.sv.j2`**: UVM monitor with TLM port
- **`sequencer.sv.j2`**: UVM sequencer and base sequence
- **`agent.sv.j2`**: UVM agent
- **`scoreboard.sv.j2`**: UVM scoreboard
- **`env_generated.sv.j2`**: UVM environment
- **`test.sv.j2`**: Base test
- **`interface.sv.j2`**: SystemVerilog interface
- **`tb_top.sv.j2`**: Top-level testbench (if provided, else fallback used)

Each template receives context with:
- `module`: DUT module name
- `topname`: Testbench top module name
- `ports`: Full list of `Port` objects
- `input_ports`: Ports with direction="input"
- `output_ports`: Ports with direction="output"
- `inout_ports`: Ports with direction="inout"

## Testing

Run the unit tests:

```bash
pip install pytest
py -m pytest
```

Tests cover:
- Basic file generation
- Full UVM component generation
- Port parsing (direction, widths)
- Edge cases (no ports, complex declarations)
- Signal declarations with proper widths

## Customization

### Modify Templates

Edit templates in the `templates/` directory to customize generated components. Examples:
- Add additional TLM connections in `agent.sv.j2`
- Implement specific stimulus logic in `sequencer.sv.j2`
- Add custom scoreboard checks in `scoreboard.sv.j2`

### Extend Generator

Subclass `TBGenerator` to add custom generation logic:

```python
class CustomGenerator(TBGenerator):
    def generate(self):
        super().generate()
        # Add custom generation logic
```

## Limitations

- Heuristic parser handles common Verilog styles but may not support all edge cases.
- Parameterized modules not yet supported.
- Complex port types (structs, etc.) not supported.
- Requires standard UVM package (`uvm_pkg`) and macros.

## Future Enhancements

- Full UVM agent generation with advanced features
- Support for parameterized modules
- Advanced port type handling (arrays, structs)
- Configuration class generation
- Automatic testbench regression framework
- VIP (Verification IP) template library

## License

MIT
