import sys
import math
import argparse

def define_1d_mesh(x_min_approx, x_max_approx, bin_width_approx, boundary1, boundary2):
    """
    A Python function that defines a 1D mesh

    User provides:
    * Approximate mesh range (x_min_approx, x_max_approx)
    * Approximate bin width (bin_width_approx)
    * Two exact boundary points (boundary1, boundary2) that must align with bin edges
    * The function adjusts the range and number of bins so that both boundary points fall exactly on bin edges.

    Returns: (x_min, x_max, num_bins, bin_width)
    """
    # Ensure boundary1 < boundary2
    b1, b2 = sorted((boundary1, boundary2))

    # Start by placing bin edges so that both b1 and b2 lie exactly on edges
    # Try candidate bin widths that fit exactly between b1 and b2
    span = b2 - b1
    best = None
    min_diff = float('inf')

    for n_bins_between in range(1, 1000):  # try reasonable number of bins
        candidate_width = span / n_bins_between
        diff = abs(candidate_width - bin_width_approx)
        if diff < min_diff:
            min_diff = diff
            best = (n_bins_between, candidate_width)

    n_between, final_bin_width = best

    # Now extend left and right from b1 and b2 to cover the full approximate range
    n_left = math.ceil((b1 - x_min_approx) / final_bin_width)
    n_right = math.ceil((x_max_approx - b2) / final_bin_width)

    # Compute final mesh range
    x_min = b1 - n_left * final_bin_width
    x_max = b2 + n_right * final_bin_width
    total_bins = n_left + n_between + n_right

    return round(x_min, 8), round(x_max, 8), total_bins, round((x_max-x_min)/total_bins, 8)


def main():

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('xmin_approx', type=float, help='approximate value of mesh min boundary')
    parser.add_argument('xmax_approx', type=float, help='approximate value of mesh max boundary')
    parser.add_argument('width_approx', type=float, help='approximate value of mesh bin width')
    parser.add_argument('edge1', type=float, help='exact value of the first boundary')
    parser.add_argument('edge2', type=float, help='exact value of the second boundary')

    args = parser.parse_args()

    x_min_approx = args.xmin_approx
    x_max_approx = args.xmax_approx
    bin_width_approx = args.width_approx
    boundary1 = args.edge1
    boundary2 = args.edge2

    x_min, x_max, num_bins, bin_width = define_1d_mesh(x_min_approx, x_max_approx, bin_width_approx, boundary1, boundary2)

    print(f"min: {x_min}\tmax: {x_max}\tnbins: {num_bins}\tbin width: {bin_width=}")

    # edges = [x_min + i * (x_max - x_min) / num_bins for i in range(num_bins + 1)]
    # print(edges)

if __name__ == "__main__":
    sys.exit(main())
