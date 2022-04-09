# Simple usage
# python3 -m pifive factorial.py

# Other options...
# python3 -m <input.py> -o <output.s> <-p print> <-c comments>

import argparse as ap
import pifive_module as pifive

def run_pifive(args):
  pifive.run_pifive(args.input, args.print, args.comments, args.output)

# Add arguments to argument parser 
parser = ap.ArgumentParser()
parser.add_argument("input", help="input python file")
parser.add_argument("-p", "--print", help="prints the output to the console", action="store_true")
parser.add_argument("-c", "--comments", help="turn on assembly comments", action="store_true")
parser.add_argument("-o", "--output", help="write the output to the file", type=str, default="output.s")
parser.set_defaults(func=run_pifive)
args = parser.parse_args()

# Run the default function with parsed arguments
args.func(args) 