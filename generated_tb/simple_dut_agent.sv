class simple_dut_agent extends uvm_agent;
  `uvm_component_utils(simple_dut_agent)

  simple_dut_driver drv;
  simple_dut_sequencer sqr;
  simple_dut_monitor mon;

  function new(string name, uvm_component parent);
    super.new(name, parent);
  endfunction

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    drv = simple_dut_driver::type_id::create("drv", this);
    sqr = simple_dut_sequencer::type_id::create("sqr", this);
    mon = simple_dut_monitor::type_id::create("mon", this);
  endfunction

  function void connect_phase(uvm_phase phase);
    super.connect_phase(phase);
    drv.seq_item_port.connect(sqr.seq_item_export);
  endfunction
endclass