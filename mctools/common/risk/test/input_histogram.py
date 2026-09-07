import ROOT


def create_test_histogram(
    name: str = "th3", scale: float = 1.0, dx=0.0, dy=0.0, dz=0.0
) -> ROOT.TH3F:
    hist = ROOT.TH3F(
        name,
        name,
        2,
        -1.0 + dx,
        1.0 + dx,
        2,
        -1.0 + dy,
        1.0 + dy,
        2,
        -1.0 + dz,
        1.0 + dz,
    )
    value = 0.0
    for i in range(2):
        for j in range(2):
            for k in range(2):
                hist.SetBinContent(i + 1, j + 1, k + 1, scale * value)
                hist.SetBinError(i + 1, j + 1, k + 1, scale * value * 0.1)
                value += 1.0
    return hist
