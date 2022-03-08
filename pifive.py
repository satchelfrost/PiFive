import argparse as ap
import pifive_module as pifive

def run_pifive(args):
    pifive.run_pifive(args.input_file)

def run_tests(args):
    pifive.run_tests()

# Add arguments to argument parser 
parser = ap.ArgumentParser()
subparser = parser.add_subparsers(title="subcommands")

# Run subcommand
run_parser = subparser.add_parser("run", help="runs the PiFive transpiler")
run_parser.add_argument("-i", "--input", help="input python file", type=str)
parser.set_defaults(func=run_pifive)

# Test subcommand
test_parser = subparser.add_parser("test", help="runs tests on RISC-V transpiler")
test_parser.set_defaults(func=run_tests)

args = parser.parse_args()

# Run the default function with parsed arguments
args.func(args) 