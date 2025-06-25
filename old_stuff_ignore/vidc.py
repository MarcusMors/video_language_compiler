
# ------------------------------------------------------------------------------
# usage: vidc.py [-h] [--xLabel [XLABEL]] [--title [TITLE]]
#                [--series SERIES [SERIES ...]]
#                INPUT [INPUT ...]

# VID Compiler - Transpile .vid to Python

# positional arguments:
#   INPUT                 input file name

# optional arguments:
#   -h, --help            show this help message and exit

# ------------------------------------------------------------------------------
# Example call:
# python3 vidc.py input_file.vid -o output_file.py
# ------------------------------------------------------------------------------

import argparse

from compiler import *


def set_partser_arguments():
    parser = argparse.ArgumentParser(
        description="VID Compiler - Transpile .vid to Python",
        epilog="script designed by José Vilca <@marcusmors> and @bryanzuca",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "input",
        metavar="<file>",
        type=str,
        nargs=1,
        help="The .vid source file to compile",
        # required=True,
    )

    # Optional output file
    parser.add_argument(
        "-o", "--output",
        metavar="<output>",
        default="output.py",
        type=str,
        nargs=1,
        help="The output .py file",
        # required=True,
    )

    # Optional verbose flag that accepts multiple comma-separated values
    parser.add_argument(
        "--verbose",
        help="Enable verbose output for specific stages (e.g., ast, scanner)",
        type=lambda s: [v.strip() for v in s.split(",")],
        default=[]
    )

    args = parser.parse_args()

    print(f"Input file: {args.input}")
    print(f"Output file: {args.output}")
    print(f"Verbose flags: {args.verbose}")

    # Example of how you might use the flags
    if "scanner" in args.verbose:
        print("[Verbose] Scanner stage enabled")

    if "ast" in args.verbose:
        print("[Verbose] AST stage enabled")

    return parser


def main():
    parser = set_partser_arguments()
    args = parser.parse_args()
    
    vidc = Compiler(args.input, args.output, args.verbose)
    vidc.compile()
    # compile_vid_file(args.input, args.output, args.verbose)

if __name__ == "__main__":
    main()
