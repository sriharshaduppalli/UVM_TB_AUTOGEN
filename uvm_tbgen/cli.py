import argparse
from .generator import TBGenerator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="uvm-tbgen")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate a UVM testbench")
    gen.add_argument("--dut", required=True, help="Path to DUT Verilog file")
    gen.add_argument("--outdir", default="generated_tb", help="Output directory")
    gen.add_argument("--topname", default="my_dut_tb", help="Top-level testbench name")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
        gen = TBGenerator(dut_path=args.dut, outdir=args.outdir, topname=args.topname)
        gen.generate()
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
