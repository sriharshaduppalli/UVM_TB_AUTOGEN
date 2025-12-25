class simple_dut_test extends uvm_test;
  `uvm_component_utils(simple_dut_test)

  simple_dut_env env;

  function new(string name, uvm_component parent);
    super.new(name, parent);
  endfunction

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    env = simple_dut_env::type_id::create("env", this);
  endfunction

  task run_phase(uvm_phase phase);
    phase.raise_objection(this);
    #1000;
    phase.drop_objection(this);
  endtask
endclass