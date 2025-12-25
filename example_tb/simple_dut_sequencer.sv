class simple_dut_sequencer extends uvm_sequencer #(simple_dut_seq_item);
  `uvm_component_utils(simple_dut_sequencer)

  function new(string name, uvm_component parent);
    super.new(name, parent);
  endfunction
endclass


class simple_dut_base_seq extends uvm_sequence #(simple_dut_seq_item);
  `uvm_object_utils(simple_dut_base_seq)

  function new(string name = "simple_dut_base_seq");
    super.new(name);
  endfunction

  task body();
    repeat(10) begin
      simple_dut_seq_item item = simple_dut_seq_item::type_id::create("item");
      start_item(item);
      // Randomize or set stimulus here      item.clk = $urandom();      item.rst_n = $urandom();      item.in_data = $urandom();      finish_item(item);
      $display("[simple_dut_base_seq] Sequence item generated");
    end
  endtask
endclass