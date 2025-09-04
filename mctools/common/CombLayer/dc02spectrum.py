#!/usr/bin/env python

import sys
import argparse

EXPECTED_UNITS = ["eV", "ph/s/mr^2/0.1%", "F.Dens/mm^2", "ph/s/0.1%", "ph/s/eV", "ph/s", "kW", "m", "m", "rad", "rad"]

Q_E = 1.6021766208e-19  # [Coulombs]


def check_units(words):
    """Return True if the given list of words matches the expected header units."""
    return words == EXPECTED_UNITS

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process undulator team data to compute flux and energy scaling.",
        epilog="Homepage: https://github.com/kbat/mc-tools"
    )
    parser.add_argument("dc0", type=str, help="Data file from the undulator team")
    parser.add_argument("-energy", type=int, default=0, help="Energy column index (0-based)")
    parser.add_argument("-flux", type=int, default=3, help="Flux column index (0-based)")
    parser.add_argument("-divx", type=int, default=9, help="X divergence column index (0-based)")
    parser.add_argument("-divy", type=int, default=10, help="Y divergence column index (0-based)")
    parser.add_argument("-happ", type=float, required=True, help="Last FM horizontal aperture [rad]")
    parser.add_argument("-vapp", type=float, required=True, help="Last FM vertical aperture [rad]")
    parser.add_argument("-power", type=float, default=1200.0, help="Beam power guess [W]")
    return parser.parse_args()

def process_file(filename, args):
    """Process the input data file and compute energy sums."""
    data_started = False
    sum_b = sum_c = 0.0
    e_prev = 0.0

    with open(filename) as f:
        for line_no, line in enumerate(f, 1):
            words = line.strip().split()

            # Detect header line with units
            if len(words) == len(EXPECTED_UNITS) and check_units(words):
                data_started = True
                continue

            if not data_started or not words:
                continue

            try:
                energy = float(words[args.energy])
                flux = float(words[args.flux])
                h_size = float(words[args.divx])
                v_size = float(words[args.divy])
            except (ValueError, IndexError):
                print(f"Warning: Skipping malformed line {line_no}", file=sys.stderr)
                continue

            e_gap = energy - e_prev
            y = flux / (energy * 0.001)  # eV/ph/s/0.1%
            a_scale = 1.0
            if h_size < args.happ:
                a_scale *= args.happ / h_size
            if v_size < args.vapp:
                a_scale *= args.vapp / v_size

            value = y * e_gap * a_scale
            print(f"{energy:.6g} {value:.6e}")

            sum_b += energy * value
            sum_c += y * e_gap

            e_prev = energy

    return sum_b, sum_c

def main():
    args = parse_arguments()
    sum_b, sum_c = process_file(args.dc0, args)

    if sum_c == 0:
        print("Error: No valid data processed.", file=sys.stderr)
        return 1

    print(f"Energy: {sum_b * Q_E:.6e}", file=sys.stderr)
    print(f"Sum: {sum_c * Q_E:.6e}", file=sys.stderr)
    print(f"Div: {args.power / (sum_c * Q_E):.6f}", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
