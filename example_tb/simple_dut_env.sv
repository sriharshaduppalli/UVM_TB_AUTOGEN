class simple_dut_env extends uvm_env;
  `uvm_component_utils(simple_dut_env)

  simple_dut_agent agt;
  simple_dut_scoreboard sb;

  function new(string name, uvm_component parent);
    super.new(name, parent);
  endfunction

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    agt = simple_dut_agent::type_id::create("agt", this);
    sb = simple_dut_scoreboard::type_id::create("sb", this);
  endfunction

  function void connect_phase(uvm_phase phase);
    super.connect_phase(phase);
    // Connect monitor to scoreboard
    agt.mon.ap.connect(sb.mon_export);
  endfunction
endclass