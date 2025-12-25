class simple_dut_monitor extends uvm_monitor;
  `uvm_component_utils(simple_dut_monitor)

  virtual simple_dut_if vif;
  uvm_analysis_port #(simple_dut_seq_item) ap;

  function new(string name, uvm_component parent);
    super.new(name, parent);
    ap = new("ap", this);
  endfunction

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    if (!uvm_config_db#(virtual simple_dut_if)::get(this, "", "vif", vif))
      `uvm_fatal("NOVIF", "Virtual interface not found")
  endfunction

  task run_phase(uvm_phase phase);
    forever begin
      @(posedge vif.clk);
      begin
        simple_dut_seq_item item = simple_dut_seq_item::type_id::create("item");
        // Collect signals from DUT interface        item.clk = vif.clk;        item.rst_n = vif.rst_n;        item.in_data = vif.in_data;        ap.write(item);
        $display("[simple_dut_monitor] Observed transaction");
      end
    end
  endtask
endclass