import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from climate_evidence_bench.units import UnitDimensionMismatch, UnsupportedUnit, convert


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


if __name__ == "__main__":
    unittest.main()
