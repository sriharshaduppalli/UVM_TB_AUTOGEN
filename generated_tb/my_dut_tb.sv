// Auto-generated UVM testbench top (fallback)
`timescale 1ns/1ps
`include "uvm_macros.svh"
import uvm_pkg::*;

module my_dut_tb;

  // DUT interface
  simple_dut_if dut_if();

  // DUT instance
  simple_dut dut_inst (
    .clk(dut_if.clk),
    .rst_n(dut_if.rst_n),
    .in_data(dut_if.in_data),
    .reg(dut_if.reg),
    .valid(dut_if.valid)
  );

  initial begin
    run_test();
  end
endmodule
