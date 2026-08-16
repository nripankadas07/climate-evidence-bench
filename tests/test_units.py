import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from climate_evidence_bench.units import (
    ALIASES,
    UnitDimensionMismatch,
    UnsupportedUnit,
    convert,
    describe,
)


class UnitTests(unittest.TestCase):
    def test_emissions_conversion(self):
        self.assertEqual(convert(2400.0, "ktCO2e", "MtCO2e"), 2.4)

    def test_area_conversion(self):
        self.assertEqual(convert(12.5, "km2", "ha"), 1250.0)

    def test_dimension_mismatch(self):
        with self.assertRaises(UnitDimensionMismatch):
            convert(1.0, "GWh", "tCO2e")

    def test_unsupported_unit(self):
        with self.assertRaises(UnsupportedUnit):
            convert(1.0, "mystery", "tCO2e")

    def test_dimensional_operator_is_not_erased(self):
        with self.assertRaises(UnsupportedUnit):
            convert(1.0, "kW/h", "kWh")

    def test_every_alias_preserves_finite_identity_extremes_exactly(self):
        values = (
            sys.float_info.max,
            1e308,
            sys.float_info.min,
            math.ulp(0.0),
            -sys.float_info.max,
            -1e308,
            -sys.float_info.min,
            -math.ulp(0.0),
            0.0,
            -0.0,
        )
        for alias in sorted(ALIASES):
            for value in values:
                with self.subTest(alias=alias, value=value):
                    converted = convert(value, alias, alias)
                    self.assertEqual(converted, value)
                    if value == 0.0:
                        self.assertEqual(
                            math.copysign(1.0, converted),
                            math.copysign(1.0, value),
                        )

    def test_every_same_dimension_alias_pair_uses_the_precomputed_ratio(self):
        aliases_by_dimension = {}
        for alias in sorted(ALIASES):
            aliases_by_dimension.setdefault(describe(alias)[0], []).append(alias)
        values = (
            sys.float_info.max,
            1e308,
            sys.float_info.min,
            math.ulp(0.0),
            -sys.float_info.max,
            -1e308,
            -sys.float_info.min,
            -math.ulp(0.0),
            0.0,
        )
        for aliases in aliases_by_dimension.values():
            for from_unit in aliases:
                from_factor = describe(from_unit)[1]
                for to_unit in aliases:
                    to_factor = describe(to_unit)[1]
                    ratio = from_factor / to_factor
                    for value in values:
                        with self.subTest(
                            from_unit=from_unit,
                            to_unit=to_unit,
                            value=value,
                        ):
                            expected = value if from_factor == to_factor else value * ratio
                            converted = convert(value, from_unit, to_unit)
                            if math.isnan(expected):
                                self.assertTrue(math.isnan(converted))
                            else:
                                self.assertEqual(converted, expected)


if __name__ == "__main__":
    unittest.main()
