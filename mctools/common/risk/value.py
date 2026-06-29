import warnings


class Value:
    def __init__(
        self,
        val: float,
        err: float,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        threshold: float = float("-inf"),
    ):
        self.val = val
        self.err = err
        self.relerr = 100.0
        if val != 0.0:
            if val >= threshold:
                self.relerr = 100.0 * err / abs(val)
            else:
                warnings.warn(
                    f"Value smaller than the user-defined threshold of {threshold} "
                    "encountered. Arbitrarily setting its relative uncertainty to 100%."
                )
        else:
            self.relerr = float("inf")
        self.x = x
        self.y = y
        self.z = z

    def __gt__(self, other):
        if isinstance(other, Value):
            return self.val > other.val
        return NotImplemented

    def __str__(self):
        return f"{self.val:.3g} ± {self.err:.1g}   {self.relerr:.1f} %"

    def __repr__(self):
        return f"Value({self.val}, {self.err})"


class UnknownValue(Value):
    def __init__(self):
        super().__init__(val=0.0, err=0.0)
