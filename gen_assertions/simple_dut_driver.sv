class simple_dut_driver extends uvm_driver;
  `uvm_component_utils(simple_dut_driver)

  virtual simple_dut_if vif;
  simple_dut_seq_item item;

  function new(string name, uvm_component parent);
    super.new(name, parent);
  endfunction

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    if (!uvm_config_db#(virtual simple_dut_if)::get(this, "", "vif", vif))
      `uvm_fatal("NOVIF", "Virtual interface not found")
  endfunction

  task run_phase(uvm_phase phase);
    forever begin
      @(posedge vif.clk);
      $display("[simple_dut_driver] Driving stimulus");
    end
  endtask
endclass