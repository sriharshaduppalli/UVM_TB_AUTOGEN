// Auto-generated Checker module for simple_dut
// Behavioral and protocol checking

class simple_dut_checker extends uvm_component;
  `uvm_component_utils(simple_dut_checker)

  // Virtual interface
  virtual simple_dut_if vif;

  // Checkers  reset_checker_i reset_chk;  protocol_checker_i valid_chk;
  // Check count and error tracking
  int check_count = 0;
  int error_count = 0;
  string violation_log[$];

  // Checker properties
  property p_no_x_on_outputs;
    @(posedge vif.clk) disable iff(!vif.rst_n)
    !$isunknown(vif.reg);
  endproperty
  a_no_x_on_outputs: assert property(p_no_x_on_outputs)
    else begin
      error_count++;
      violation_log.push_back("X found on output signals");
    end  // Valid pulse should be narrow (typically 1-2 cycles)
  property p_valid_pulse_width;
    @(posedge vif.clk) disable iff(!vif.rst_n)
    (vif.valid && !$past(vif.valid)) |-> ##[0:10] (!vif.valid);
  endproperty
  a_valid_pulse_width: assert property(p_valid_pulse_width)
    else begin
      error_count++;
      violation_log.push_back("Valid pulse too wide");
    end  // Reset should clear all outputs
  property p_reset_clears_outputs;
    @(posedge rst_n)    (reg == 0) &&    (valid == 0) &&    1;
  endproperty
  a_reset_clears_outputs: assert property(p_reset_clears_outputs)
    else begin
      error_count++;
      violation_log.push_back("Outputs not cleared after reset");
    end
  function new(string name, uvm_component parent);
    super.new(name, parent);
  endfunction

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    if (!uvm_config_db#(virtual simple_dut_if)::get(this, "", "vif", vif))
      `uvm_fatal("NOVIF", "Virtual interface not configured")
  endfunction

  virtual function void start_of_simulation_phase(uvm_phase phase);
    super.start_of_simulation_phase(phase);
    `uvm_info(get_type_name(), "Starting behavioral checking", UVM_LOW)
  endfunction

  virtual function void check_reset_sequence();
    // Monitor reset behavior
    if (vif.rst_n == 0) begin
      check_count++;
      // Verify outputs are cleared      if (vif.reg != 0) begin
        error_count++;
        `uvm_error("CHK_RESET", $sformatf("Output reg not cleared: %0d", vif.reg))
        violation_log.push_back("reg not cleared");
      end      if (vif.valid != 0) begin
        error_count++;
        `uvm_error("CHK_RESET", $sformatf("Output valid not cleared: %0d", vif.valid))
        violation_log.push_back("valid not cleared");
      end    end
  endfunction

  virtual function void check_output_validity();
    // Verify outputs are valid (not X)    if ($isunknown(vif.reg)) begin
      error_count++;
      `uvm_error("CHK_INVALID", "Output reg contains X")
      violation_log.push_back("X on reg");
    end    if ($isunknown(vif.valid)) begin
      error_count++;
      `uvm_error("CHK_INVALID", "Output valid contains X")
      violation_log.push_back("X on valid");
    end  endfunction  virtual function void check_valid_protocol();
    // Valid signal should not be stuck high
    static int valid_high_cycles = 0;
    
    if (vif.valid) begin
      valid_high_cycles++;
      if (valid_high_cycles > 100) begin
        error_count++;
        `uvm_error("CHK_VALID_STUCK", "Valid signal stuck high")
        violation_log.push_back("Valid stuck high");
        valid_high_cycles = 0;
      end
    end else begin
      valid_high_cycles = 0;
    end
  endfunction
  virtual function void check_protocol_compliance();
    check_reset_sequence();
    check_output_validity();    check_valid_protocol();  endfunction

  virtual function int get_error_count();
    return error_count;
  endfunction

  virtual function int get_check_count();
    return check_count;
  endfunction

  virtual function string get_violation_log();
    string log = "";
    foreach(violation_log[i]) begin
      log = {log, violation_log[i], "\n"};
    end
    return log;
  endfunction

  virtual function void report_phase(uvm_phase phase);
    super.report_phase(phase);
    `uvm_info(get_type_name(),
      $sformatf("Checks Performed: %0d | Violations Found: %0d",
        check_count, error_count), UVM_LOW)
    if (error_count > 0) begin
      `uvm_info(get_type_name(), $sformatf("Violations:\n%s", get_violation_log()), UVM_LOW)
    end
  endfunction

endclass

// Lightweight checker interface for inline checkers
module simple_dut_inline_checker (
  input clk,
  input rst_n,
  input [7:0] in_data,
  input reg,
  input valid);

  // Parameter checking  property p_output_not_x;
    @(posedge clk) disable iff(!rst_n)
    !$isunknown(reg);
  endproperty
  a_output_not_x: assert property(p_output_not_x)
    else $error("Output reg contains X value");
  // Reset propagation check
  property p_reset_effect;
    @(negedge rst_n)
    rst_n == 0;
  endproperty
  a_reset_effect: assert property(p_reset_effect)
    else $error("Reset signal error");  // Handshake protocol check
  property p_valid_not_stuck_check;
    @(posedge clk) disable iff(!rst_n)
    valid |-> ##[1:50] !valid;
  endproperty
  a_valid_not_stuck_check: assert property(p_valid_not_stuck_check)
    else $error("Valid signal appears to be stuck");
endmodule

// Coverage and checking integration
bind simple_dut simple_dut_inline_checker checker_inst (
  .clk(clk),
  .rst_n(rst_n),
  .in_data(in_data),
  .reg(reg),
  .valid(valid));