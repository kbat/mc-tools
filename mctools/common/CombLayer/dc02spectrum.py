#!/usr/bin/env python

import sys
import argparse

Q_E = 1.6021766208e-19  # [Coulombs]

def get_expected_units(beamline):
    if beamline == "SoftiMAX":
        return ["eV", "ph/s/mr^2/0.1%", "F.Dens/mm^2", "ph/s/0.1%", "ph/s/eV", "ph/s", "kW", "m", "m", "rad", "rad"]
    if beamline == "TomoWISE":
        return ["eV", "ph/s/mr^2/0.1%", "F.Dens/mm^2", "ph/s/0.1%", "m", "rad", "m", "m", "rad", "rad", "ph/s/0.1%","W", "-", "-", "-"]

def check_units(beamline, words):
    """Return True if the given list of words matches the expected header units."""
    EXPECTED_UNITS = get_expected_units(beamline)
    return len(words) == len(EXPECTED_UNITS) and words == EXPECTED_UNITS

def get_flux_column(beamline):
    "Return the flux column index (0-based)"
    EXPECTED_UNITS = get_expected_units(beamline)
    try:
        idx = EXPECTED_UNITS.index("ph/s/0.1%")
    except ValueError:
        idx = None
        print("Error: Unknown beamline:", beamline, file=sys.stderr)
        sys.exit(1)

    return idx

def get_divx_column(beamline):
    "Return the Div.x column index (0-based)"
    if beamline == "SoftiMAX":
        return 9
    if beamline == "TomoWISE":
        return 8

    print("Error: Unknown beamline:", beamline, file=sys.stderr)
    sys.exit(1)

def get_divy_column(beamline):
    "Return the Div.y column index (0-based)"
    if beamline == "SoftiMAX":
        return 10
    if beamline == "TomoWISE":
        return 9

    print("Error: Unknown beamline:", beamline, file=sys.stderr)
    sys.exit(1)

def get_power_guess(beamline):
    "Return the guess value of the power [W]"
    if beamline == "SoftiMAX":
        return 1200.0
    if beamline == "TomoWISE":
        print("Check power guess", file=sys.stderr)
        return 1200.0

    print("Error: Unknown beamline [get_power_guess]:", beamline, file=sys.stderr)
    sys.exit(1)

def get_horizontal_aperture(beamline, insertion_device):
    "Return horizontal aperture of last FM [rad]"
    if beamline == "SoftiMAX":
        return 220e-6
    if beamline == "TomoWISE":
        if insertion_device == "CPMU":
            return 0.1e-3 # 0.1 mrad due to MSM in the undulator mode

    print("Error: Unknown beamline [get_horizontal_aperture]:", beamline, file=sys.stderr)
    sys.exit(1)

def get_vertical_aperture(beamline, insertion_device):
    "Return vertical aperture of last FM [rad]"
    if beamline == "SoftiMAX":
        return 220e-6
    if beamline == "TomoWISE":
        if insertion_device == "CPMU":
            return 0.1e-3 # 0.1 mrad due to FM2

    print("Error: Unknown beamline [get_vertical_aperture]:", beamline, file=sys.stderr)
    sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process undulator team data to compute flux and energy scaling.",
        epilog="Homepage: https://github.com/kbat/mc-tools"
    )
    parser.add_argument("dc0", type=str, help="Data file from the undulator team")
    parser.add_argument("-beamline", type=str, default="TomoWISE", help="Beamline name")
    parser.add_argument("-id", type=str, default="", help="Insertion device (only for multi-ID beamlines)0.")

    args = parser.parse_args()

    if args.beamline == "TomoWISE" and args.id == "":
        print(f"Error: {args.beamline} insertion device is not specified", file=sys.stderr)
        sys.exit(1)

    return args

def process_file(filename, args):
    """Process the input data file and compute energy sums."""
    data_started = False
    sum_b = sum_c = 0.0
    e_prev = 0.0

    happ = get_horizontal_aperture(args.beamline, args.id)
    vapp = get_vertical_aperture(args.beamline, args.id)

    flux_column = get_flux_column(args.beamline)
    divx_column = get_divx_column(args.beamline)
    divy_column = get_divy_column(args.beamline)

    with open(filename) as f:
        for line_no, line in enumerate(f, 1):
            words = line.strip().split()

            # Detect header line with units
            if check_units(args.beamline, words):
                data_started = True
                continue

            if not data_started or not words:
                continue

            try:
                energy = float(words[0])
                flux = float(words[flux_column])
                h_size = float(words[divx_column])
                v_size = float(words[divy_column])
            except (ValueError, IndexError):
                print(f"Warning: Skipping malformed line {line_no}", file=sys.stderr)
                continue

            e_gap = energy - e_prev # eV
            y = flux / (energy * 0.001)  # eV/ph/s/0.1%
            a_scale = 1.0
            if h_size < happ:
                a_scale *= happ / h_size
            if v_size < vapp:
                a_scale *= vapp / v_size

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
    print(f"Div: {get_power_guess(args.beamline) / (sum_c * Q_E):.6f}", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
