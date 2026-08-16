"""Small explicit unit registry and conversion helpers."""

from typing import Dict, Tuple


class UnitError(ValueError):
    """Base class for unit evaluation errors."""


class UnsupportedUnit(UnitError):
    pass


class UnitDimensionMismatch(UnitError):
    pass


# factor converts a value to the dimension's base unit.
REGISTRY: Dict[str, Tuple[str, float, str]] = {
    "kgco2e": ("emissions", 0.001, "kgCO2e"),
    "tco2e": ("emissions", 1.0, "tCO2e"),
    "ktco2e": ("emissions", 1_000.0, "ktCO2e"),
    "mtco2e": ("emissions", 1_000_000.0, "MtCO2e"),
    "wh": ("energy", 0.001, "Wh"),
    "kwh": ("energy", 1.0, "kWh"),
    "mwh": ("energy", 1_000.0, "MWh"),
    "gwh": ("energy", 1_000_000.0, "GWh"),
    "fraction": ("ratio", 1.0, "fraction"),
    "%": ("ratio", 0.01, "%"),
    "percent": ("ratio", 0.01, "%"),
    "ha": ("area", 1.0, "ha"),
    "km2": ("area", 100.0, "km2"),
    "m3": ("volume", 1.0, "m3"),
    "l": ("volume", 0.001, "L"),
}

# Exact, reviewed spellings only. Operators are semantic: for example, kW/h is
# not an alias for kWh and therefore remains unsupported.
ALIASES = {
    "kgco2e": "kgco2e",
    "kg co2e": "kgco2e",
    "tco2e": "tco2e",
    "t co2e": "tco2e",
    "ktco2e": "ktco2e",
    "kt co2e": "ktco2e",
    "mtco2e": "mtco2e",
    "mt co2e": "mtco2e",
    "wh": "wh",
    "w h": "wh",
    "w·h": "wh",
    "kwh": "kwh",
    "kw h": "kwh",
    "kw·h": "kwh",
    "mwh": "mwh",
    "mw h": "mwh",
    "mw·h": "mwh",
    "gwh": "gwh",
    "gw h": "gwh",
    "gw·h": "gwh",
    "fraction": "fraction",
    "%": "%",
    "percent": "percent",
    "ha": "ha",
    "km2": "km2",
    "km^2": "km2",
    "km²": "km2",
    "m3": "m3",
    "m^3": "m3",
    "m³": "m3",
    "l": "l",
}


def _key(unit: str) -> str:
    if not isinstance(unit, str) or not unit.strip():
        raise UnsupportedUnit("unit must be a non-empty string")
    normalized = " ".join(unit.strip().casefold().split())
    try:
        return ALIASES[normalized]
    except KeyError as exc:
        raise UnsupportedUnit("unsupported unit: {0}".format(unit)) from exc


def describe(unit: str) -> Tuple[str, float, str]:
    key = _key(unit)
    return REGISTRY[key]


def convert(value: float, from_unit: str, to_unit: str) -> float:
    from_dimension, from_factor, _ = describe(from_unit)
    to_dimension, to_factor, _ = describe(to_unit)
    if from_dimension != to_dimension:
        raise UnitDimensionMismatch(
            "cannot convert {0} ({1}) to {2} ({3})".format(
                from_unit, from_dimension, to_unit, to_dimension
            )
        )
    normalized = float(value)
    if from_factor == to_factor:
        # Identity conversions must preserve every finite float exactly,
        # including the largest values and signed subnormals.
        return normalized
    factor_ratio = from_factor / to_factor
    return normalized * factor_ratio
