from pathlib import Path
from uvm_tbgen.generator import TBGenerator, _extract_module_and_ports


def test_generator_creates_files(tmp_path: Path):
    """Test basic file generation with parsed ports."""
    dut = tmp_path / "simple_dut.v"
    dut.write_text(
        """
module simple_dut(input clk, input rst, input [3:0] inbus, output [7:0] outbus);
  // DUT body
endmodule
""",
        encoding="utf-8",
    )

    outdir = tmp_path / "out"
    gen = TBGenerator(dut_path=str(dut), outdir=str(outdir), topname="tb")
    gen.generate()

    # Assert DUT copied
    assert (outdir / "simple_dut.v").exists()

    # Assert testbench written
    tb = outdir / "tb.sv"
    assert tb.exists()
    text = tb.read_text(encoding="utf-8")
    assert "simple_dut" in text


def test_full_uvm_generation(tmp_path: Path):
    """Test complete UVM component generation."""
    dut = tmp_path / "test_dut.v"
    dut.write_text(
        """
module test_dut(
  input clk,
  input [7:0] data_in,
  output [15:0] data_out
);
endmodule
""",
        encoding="utf-8",
    )

    outdir = tmp_path / "out"
    gen = TBGenerator(dut_path=str(dut), outdir=str(outdir), topname="my_tb")
    gen.generate()

    # Verify all components generated
    assert (outdir / "test_dut_seq_item.sv").exists()
    assert (outdir / "test_dut_driver.sv").exists()
    assert (outdir / "test_dut_monitor.sv").exists()
    assert (outdir / "test_dut_sequencer.sv").exists()
    assert (outdir / "test_dut_agent.sv").exists()
    assert (outdir / "test_dut_scoreboard.sv").exists()
    assert (outdir / "test_dut_env.sv").exists()
    assert (outdir / "test_dut_test.sv").exists()
    assert (outdir / "test_dut_if.sv").exists()
    assert (outdir / "my_tb.sv").exists()

    # Verify seq_item content
    seq_item_text = (outdir / "test_dut_seq_item.sv").read_text(encoding="utf-8")
    assert "rand logic [7:0] data_in" in seq_item_text
    assert "logic [15:0] data_out" in seq_item_text

    # Verify driver content
    driver_text = (outdir / "test_dut_driver.sv").read_text(encoding="utf-8")
    assert "test_dut_driver extends uvm_driver" in driver_text
    assert "test_dut_if vif" in driver_text

    # Verify environment content
    env_text = (outdir / "test_dut_env.sv").read_text(encoding="utf-8")
    assert "test_dut_agent agt" in env_text
    assert "test_dut_scoreboard sb" in env_text


def test_no_ports_module(tmp_path: Path):
    """Test generation for a module with no ports."""
    dut = tmp_path / "no_ports.v"
    dut.write_text(
        """
module no_ports;
  // DUT body with no ports
endmodule
""",
        encoding="utf-8",
    )

    outdir = tmp_path / "out"
    gen = TBGenerator(dut_path=str(dut), outdir=str(outdir), topname="tb_no_ports")
    gen.generate()

    # Should still generate all components
    assert (outdir / "no_ports_seq_item.sv").exists()
    assert (outdir / "tb_no_ports.sv").exists()


def test_port_direction_parsing(tmp_path: Path):
    """Test parsing of input, output, and inout ports."""
    dut = tmp_path / "multi_dir.v"
    dut.write_text(
        """
module multi_dir(
  input clk,
  input [7:0] data_in,
  output reg [7:0] data_out,
  inout [3:0] bus
);
endmodule
""",
        encoding="utf-8",
    )

    text = dut.read_text(encoding="utf-8")
    module_name, ports = _extract_module_and_ports(text)

    assert module_name == "multi_dir"
    assert len(ports) >= 3

    port_dict = {p.name: p for p in ports}
    assert "clk" in port_dict
    assert port_dict["clk"].direction == "input"
    assert port_dict["clk"].width == 1


def test_port_widths(tmp_path: Path):
    """Test proper parsing of port bit widths."""
    dut = tmp_path / "widths.v"
    dut.write_text(
        """
module widths(
  input [15:0] wide_in,
  output [3:0] narrow_out,
  input single
);
endmodule
""",
        encoding="utf-8",
    )

    text = dut.read_text(encoding="utf-8")
    module_name, ports = _extract_module_and_ports(text)

    port_dict = {p.name: p for p in ports}
    assert port_dict["wide_in"].width == 16
    assert port_dict["narrow_out"].width == 4
    assert port_dict["single"].width == 1


def test_complex_declarations(tmp_path: Path):
    """Test parsing of complex port declarations with wire/reg/logic."""
    dut = tmp_path / "complex.v"
    dut.write_text(
        """
module complex(
  input clk,
  input [7:0] data
);
  wire [15:0] internal;
  output [31:0] result;
endmodule
""",
        encoding="utf-8",
    )

    text = dut.read_text(encoding="utf-8")
    module_name, ports = _extract_module_and_ports(text)

    port_names = {p.name for p in ports}
    assert "clk" in port_names
    assert "data" in port_names
    assert "result" in port_names


def test_signal_declarations(tmp_path: Path):
    """Test that signal declarations use proper widths in seq_item."""
    dut = tmp_path / "sig_decl.v"
    dut.write_text(
        """
module sig_decl(
  input [7:0] byte_port,
  output single_bit
);
endmodule
""",
        encoding="utf-8",
    )

    outdir = tmp_path / "out"
    gen = TBGenerator(dut_path=str(dut), outdir=str(outdir), topname="tb")
    gen.generate()

    seq_item_text = (outdir / "sig_decl_seq_item.sv").read_text(encoding="utf-8")
    # Check for proper signal declarations with widths
    assert "[7:0] byte_port" in seq_item_text
    assert "single_bit" in seq_item_text


def test_assertions_generation(tmp_path: Path):
    """Test SVA assertions file generation."""
    dut = tmp_path / "test_dut.v"
    dut.write_text(
        """
module test_dut(
  input clk,
  input rst_n,
  input [7:0] data_in,
  output [15:0] data_out,
  output valid
);
endmodule
""",
        encoding="utf-8",
    )

    outdir = tmp_path / "out"
    gen = TBGenerator(dut_path=str(dut), outdir=str(outdir), topname="my_tb")
    gen.generate()

    # Verify assertions file generated
    assertions_file = outdir / "test_dut_assertions.sv"
    assert assertions_file.exists()

    assertions_text = assertions_file.read_text(encoding="utf-8")
    
    # Verify key assertion categories
    assert "Reset Assertions" in assertions_text
    assert "Clock Domain Crossing" in assertions_text
    assert "Output Stability" in assertions_text or "stable" in assertions_text
    assert "Protocol Properties" in assertions_text
    assert "bind test_dut" in assertions_text  # Verify bind statement


def test_assertions_patterns(tmp_path: Path):
    """Test specific assertion patterns for protocol signals."""
    dut = tmp_path / "protocol_dut.v"
    dut.write_text(
        """
module protocol_dut(
  input clk,
  input rst_n,
  input valid_in,
  output reg valid_out,
  input enable,
  output reg [7:0] data
);
endmodule
""",
        encoding="utf-8",
    )

    outdir = tmp_path / "out"
    gen = TBGenerator(dut_path=str(dut), outdir=str(outdir), topname="tb")
    gen.generate()

    assertions_text = (outdir / "protocol_dut_assertions.sv").read_text(encoding="utf-8")
    
    # Check for key assertion categories
    assert "Reset Assertions" in assertions_text
    assert "stable" in assertions_text  # Output stability assertions
    assert "bind protocol_dut" in assertions_text  # Bind statement
    assert "Input Constraints" in assertions_text
    assert "_not_glitching" in assertions_text  # Glitch prevention for inputs

def test_coverage_generation(tmp_path: Path):
    """Test coverage module generation."""
    dut = tmp_path / "test.v"
    dut.write_text(
        """
module coverage_test_dut(
  input clk,
  input rst_n,
  input [7:0] data_in,
  output reg [7:0] data_out,
  output reg valid
);
endmodule
""",
        encoding="utf-8",
    )

    outdir = tmp_path / "out"
    gen = TBGenerator(dut_path=str(dut), outdir=str(outdir), topname="tb")
    gen.generate()

    # Check coverage file generated
    coverage_file = outdir / "coverage_test_dut_coverage.sv"
    assert coverage_file.exists(), "Coverage file not generated"
    
    coverage_text = coverage_file.read_text(encoding="utf-8")
    
    # Verify coverage class exists
    assert "class coverage_test_dut_functional_coverage" in coverage_text
    assert "extends uvm_object" in coverage_text
    
    # Verify covergroups
    assert "covergroup" in coverage_text
    assert "cp_" in coverage_text  # Coverpoint prefix
    assert "get_coverage()" in coverage_text
    assert "collect_coverage()" in coverage_text
    
    # Verify coverage wrapper
    assert "class coverage_test_dut_coverage_wrapper" in coverage_text
    assert "set_virtual_interface" in coverage_text


def test_checker_generation(tmp_path: Path):
    """Test checker module generation."""
    dut = tmp_path / "test.v"
    dut.write_text(
        """
module checker_test_dut(
  input clk,
  input rst_n,
  input valid_in,
  input [15:0] data_in,
  output reg valid_out,
  output reg [15:0] data_out
);
endmodule
""",
        encoding="utf-8",
    )

    outdir = tmp_path / "out"
    gen = TBGenerator(dut_path=str(dut), outdir=str(outdir), topname="tb")
    gen.generate()

    # Check checker file generated
    checker_file = outdir / "checker_test_dut_checker.sv"
    assert checker_file.exists(), "Checker file not generated"
    
    checker_text = checker_file.read_text(encoding="utf-8")
    
    # Verify checker class
    assert "class checker_test_dut_checker extends uvm_component" in checker_text
    assert "`uvm_component_utils" in checker_text
    
    # Verify checker methods
    assert "check_protocol_compliance()" in checker_text
    assert "get_error_count()" in checker_text
    assert "get_check_count()" in checker_text
    assert "get_violation_log()" in checker_text
    
    # Verify inline checker module
    assert "module checker_test_dut_inline_checker" in checker_text
    assert "bind checker_test_dut checker_test_dut_inline_checker" in checker_text
    
    # Verify properties
    assert "property p_no_x_on_outputs" in checker_text
    assert "property p_reset_effect" in checker_text


def test_all_components_generated(tmp_path: Path):
    """Test that all 13 components are generated."""
    dut = tmp_path / "test.v"
    dut.write_text(
        """
module complete_dut(
  input clk,
  input rst_n,
  input valid,
  input [7:0] data,
  output reg ready,
  output reg [7:0] result
);
endmodule
""",
        encoding="utf-8",
    )

    outdir = tmp_path / "out"
    gen = TBGenerator(dut_path=str(dut), outdir=str(outdir), topname="tb")
    gen.generate()

    # Expected files
    expected_files = [
        "complete_dut_seq_item.sv",
        "complete_dut_driver.sv",
        "complete_dut_monitor.sv",
        "complete_dut_sequencer.sv",
        "complete_dut_agent.sv",
        "complete_dut_scoreboard.sv",
        "complete_dut_env.sv",
        "complete_dut_test.sv",
        "complete_dut_assertions.sv",
        "complete_dut_coverage.sv",
        "complete_dut_checker.sv",
        "complete_dut_if.sv",
        "tb.sv",  # Top module
    ]

    for file in expected_files:
        file_path = outdir / file
        assert file_path.exists(), f"File {file} not generated"
        content = file_path.read_text(encoding="utf-8")
        assert len(content) > 0, f"File {file} is empty"