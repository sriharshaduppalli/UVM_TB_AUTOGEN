from uvm_tbgen.generator import TBGenerator
gen = TBGenerator(dut_path="examples/simple_dut.v", outdir="generated_tb", topname="my_dut_tb")
gen.generate()
