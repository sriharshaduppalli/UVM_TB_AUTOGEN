class simple_dut_seq_item extends uvm_sequence_item;
  `uvm_object_utils(simple_dut_seq_item)

  // Input ports (stimulus)  rand logic clk;  rand logic rst_n;  rand logic [7:0] in_data;
  // Output ports (observation)  logic reg;  logic valid;
  function new(string name = "simple_dut_seq_item");
    super.new(name);
  endfunction

  function void do_copy(uvm_object rhs);
    simple_dut_seq_item item;
    if (!$cast(item, rhs))
      `uvm_error("COPY", "Failed to cast rhs to simple_dut_seq_item")    this.clk = item.clk;    this.rst_n = item.rst_n;    this.in_data = item.in_data;    this.reg = item.reg;    this.valid = item.valid;  endfunction

  function void do_print(uvm_printer printer);
    super.do_print(printer);    printer.print_field("clk", this.clk, 1);    printer.print_field("rst_n", this.rst_n, 1);    printer.print_field("in_data", this.in_data, 8);    printer.print_field("reg", this.reg, 1);    printer.print_field("valid", this.valid, 1);  endfunction
endclass