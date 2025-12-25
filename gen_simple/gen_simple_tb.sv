// Auto-generated UVM-like testbench for simple_dut.v
`timescale 1ns/1ps

module gen_simple_tb;

  // Signals for DUT ports
  logic clk;
  logic rst_n;
  logic [7:0] in_data;
  logic reg;
  logic valid;

  // Instantiate DUT
  simple_dut dut_inst (.clk(clk), .rst_n(rst_n), .in_data(in_data), .reg(reg), .valid(valid));

  // ========== UVM Scaffold (Passive Monitor) ==========
  class passive_monitor;
    virtual task run();
      $display("[passive_monitor] Monitoring simple_dut");
      // Monitor inputs:
      $monitor("[monitor] clk=%0d", clk);
      $monitor("[monitor] rst_n=%0d", rst_n);
      $monitor("[monitor] in_data=%0d", in_data);
    endtask
  endclass

  // ========== Test Harness ==========
  initial begin
    passive_monitor mon;
    mon = new();
    fork
      mon.run();
    join_none
  end

  initial begin
    $display("[gen_simple_tb] Instantiated simple_dut with 5 ports");
    #100;
    $finish;
  end

endmodule
