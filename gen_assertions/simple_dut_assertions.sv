// Auto-generated SystemVerilog Assertions for simple_dut
// These properties verify correct behavior of the DUT

module simple_dut_assertions(
  input clk,
  input rst_n,
  input [7:0] in_data,
  input reg,
  input valid);

  // ========== Reset Assertions ==========
  // After reset, the DUT should be in a known state  property p_reset_propagation;
    @(negedge rst_n) |-> @(posedge clk) 1;
  endproperty
  a_reset_propagation: assert property(p_reset_propagation)
    else $error("[simple_dut_assertions] Reset did not propagate properly");
  // ========== Clock Domain Crossing ==========
  // Output signals should be stable during the clock period (between clock edges)  property p_reg_stable;
    @(posedge clk) $stable(reg) |-> 1;
  endproperty
  a_reg_stable: assert property(p_reg_stable)
    else $warning("[simple_dut_assertions] Output reg is unstable mid-cycle");  property p_valid_stable;
    @(posedge clk) $stable(valid) |-> 1;
  endproperty
  a_valid_stable: assert property(p_valid_stable)
    else $warning("[simple_dut_assertions] Output valid is unstable mid-cycle");
  // ========== Protocol Properties ==========  // Valid signal should not remain high forever (avoid deadlock)
  property p_valid_not_stuck;
    @(posedge clk) disable iff(!rst_n)
    valid |-> ##[1:100] !valid;
  endproperty
  a_valid_not_stuck: assert property(p_valid_not_stuck)
    else $warning("[simple_dut_assertions] Valid signal appears stuck high");

  // When valid is low, monitor should not process data
  property p_valid_guards_data;
    @(posedge clk) disable iff(!rst_n)
    !valid |-> $stable(valid);
  endproperty
  a_valid_guards_data: assert property(p_valid_guards_data)
    else $info("[simple_dut_assertions] Data valid protocol check");
  // ========== Data Propagation ==========
  // ========== Output Range Constraints ==========  // Output reg should remain within valid range
  property p_reg_range_valid;
    @(posedge clk) disable iff(!rst_n)
    (reg >= 0) && (reg <= 1);
  endproperty
  a_reg_range_valid: assume property(p_reg_range_valid)
    else $warning("[simple_dut_assertions] Output reg out of range");  // Output valid should remain within valid range
  property p_valid_range_valid;
    @(posedge clk) disable iff(!rst_n)
    (valid >= 0) && (valid <= 1);
  endproperty
  a_valid_range_valid: assume property(p_valid_range_valid)
    else $warning("[simple_dut_assertions] Output valid out of range");
  // ========== Input Constraints ==========  // Input in_data should remain stable when not changing
  property p_in_data_not_glitching;
    @(posedge clk) disable iff(!rst_n)
    (in_data == $past(in_data)) |-> $stable(in_data);
  endproperty
  a_in_data_not_glitching: assume property(p_in_data_not_glitching)
    else $info("[simple_dut_assertions] Input in_data may have glitches");
  // ========== Mutual Exclusivity ==========
endmodule

// Bind the assertions module to the DUT instance in testbench
bind simple_dut simple_dut_assertions u_assertions (
  .clk(clk),
  .rst_n(rst_n),
  .in_data(in_data),
  .reg(reg),
  .valid(valid));