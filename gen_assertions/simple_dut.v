module simple_dut (
  input clk,
  input rst_n,
  input [7:0] in_data,
  output reg [7:0] out_data,
  output valid
);
  // simple pass-through
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) out_data <= 0;
    else out_data <= in_data;
  end
  assign valid = 1'b1;
endmodule