// Auto-generated Coverage module for simple_dut
// Functional coverage collection for DUT verification

class simple_dut_functional_coverage extends uvm_object;
  `uvm_object_utils(simple_dut_functional_coverage)

  // Virtual interface for coverage collection
  virtual simple_dut_if vif;

  // Covergroup for input port values  covergroup input_clk_cg;
    cp_clk: coverpoint vif.clk {
      bins low = {0};
      bins mid = {[1:127]};
      bins high = {255};
      option.auto_bin_max = 8;
      option.goal = 50;
    }
  endgroup  covergroup input_rst_n_cg;
    cp_rst_n: coverpoint vif.rst_n {
      bins low = {0};
      bins mid = {[1:127]};
      bins high = {255};
      option.auto_bin_max = 8;
      option.goal = 50;
    }
  endgroup  covergroup input_in_data_cg;
    cp_in_data: coverpoint vif.in_data {
      bins low = {0};
      bins mid = {[1:127]};
      bins high = {255};
      option.auto_bin_max = 8;
      option.goal = 50;
    }
  endgroup
  // Covergroup for output port values  covergroup output_reg_cg;
    cp_reg: coverpoint vif.reg {
      bins low = {0};
      bins mid = {[1:127]};
      bins high = {255};
      option.auto_bin_max = 8;
      option.goal = 50;
    }
  endgroup  covergroup output_valid_cg;
    cp_valid: coverpoint vif.valid {
      bins low = {0};
      bins mid = {[1:127]};
      bins high = {255};
      option.auto_bin_max = 8;
      option.goal = 50;
    }
  endgroup
  // Protocol coverage  covergroup valid_protocol_cg;
    cp_valid_pulse: coverpoint vif.valid {
      bins idle = {0};
      bins active = {1};
      option.goal = 100;
    }
  endgroup
  // Reset coverage
  covergroup reset_cg;
    cp_reset: coverpoint vif.rst_n {
      bins inactive = {1};
      bins active = {0};
      option.goal = 100;
    }
  endgroup

  // Transition coverage (state changes)
  covergroup transition_cg;
    // Track output transitions
    option.goal = 50;
  endgroup

  // Total coverage metrics
  covergroup coverage_metrics_cg;
    cp_sim_time: coverpoint $time {
      option.goal = 50;
    }
  endgroup

  // Constructor
  function new(string name = "simple_dut_functional_coverage");
    super.new(name);    input_clk_cg = new();    input_rst_n_cg = new();    input_in_data_cg = new();    output_reg_cg = new();    output_valid_cg = new();    valid_protocol_cg = new();    reset_cg = new();
    transition_cg = new();
    coverage_metrics_cg = new();
  endfunction

  // Function to collect coverage
  function void collect_coverage();    input_clk_cg.sample();    input_rst_n_cg.sample();    input_in_data_cg.sample();    output_reg_cg.sample();    output_valid_cg.sample();    valid_protocol_cg.sample();    reset_cg.sample();
    transition_cg.sample();
    coverage_metrics_cg.sample();
  endfunction

  // Function to get coverage statistics
  virtual function real get_coverage();
    real total_coverage = 0;
    int num_groups = 0;    total_coverage += input_clk_cg.get_coverage();
    num_groups++;    total_coverage += input_rst_n_cg.get_coverage();
    num_groups++;    total_coverage += input_in_data_cg.get_coverage();
    num_groups++;    total_coverage += output_reg_cg.get_coverage();
    num_groups++;    total_coverage += output_valid_cg.get_coverage();
    num_groups++;    total_coverage += valid_protocol_cg.get_coverage();
    num_groups++;    total_coverage += reset_cg.get_coverage();
    num_groups++;
    total_coverage += transition_cg.get_coverage();
    num_groups++;
    total_coverage += coverage_metrics_cg.get_coverage();
    num_groups++;

    return (num_groups > 0) ? total_coverage / num_groups : 0;
  endfunction

  // Function to print coverage report
  virtual function void print_coverage();
    `uvm_info(get_type_name(), $sformatf("Total Coverage: %0.2f%%", get_coverage()), UVM_LOW)
  endfunction

endclass

// Coverage wrapper for easy instantiation
class simple_dut_coverage_wrapper extends uvm_object;
  `uvm_object_utils(simple_dut_coverage_wrapper)

  simple_dut_functional_coverage cov;

  function new(string name = "simple_dut_coverage_wrapper");
    super.new(name);
    cov = simple_dut_functional_coverage::type_id::create("cov");
  endfunction

  virtual function void set_virtual_interface(virtual simple_dut_if vif);
    cov.vif = vif;
  endfunction

endclass