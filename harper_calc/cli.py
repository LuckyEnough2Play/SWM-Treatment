"""Calculation utilities for the Harper nutrient loading tool."""
from dataclasses import dataclass, asdict
import json


@dataclass
class SiteData:
    area_acres: float
    annual_rainfall_m: float
    runoff_coefficient: float
    emc_mg_per_L_TN: float
    emc_mg_per_L_TP: float


def calculate_runoff_volume(area_acres: float, annual_rainfall_m: float, runoff_coefficient: float) -> float:
    """Return annual runoff volume in cubic meters."""
    area_m2 = area_acres * 4046.8564224
    return annual_rainfall_m * area_m2 * runoff_coefficient


def calculate_annual_load(emc_mg_per_L: float, runoff_volume_m3: float) -> float:
    """Return annual load in kilograms."""
    return emc_mg_per_L * runoff_volume_m3 / 1000.0


def calculate_site_loads(data: SiteData) -> dict:
    """Calculate TN and TP loads for a site based on provided data."""
    runoff_volume = calculate_runoff_volume(data.area_acres, data.annual_rainfall_m, data.runoff_coefficient)
    return {
        "TN_kg_per_yr": calculate_annual_load(data.emc_mg_per_L_TN, runoff_volume),
        "TP_kg_per_yr": calculate_annual_load(data.emc_mg_per_L_TP, runoff_volume),
        "runoff_volume_m3": runoff_volume,
    }


def format_breakdown(data: SiteData, result: dict) -> str:
    """Return a multiline string showing calculation steps."""
    area_m2 = data.area_acres * 4046.8564224
    lines = [
        "Calculation Breakdown:",
        f"Runoff Volume = {data.area_acres} ac * 4046.8564224 m^2/ac = {area_m2:.2f} m^2",
        f"               * {data.annual_rainfall_m} m * {data.runoff_coefficient}",
        f"               = {result['runoff_volume_m3']:.2f} m^3",
        f"TN Load = {data.emc_mg_per_L_TN} mg/L * {result['runoff_volume_m3']:.2f} m^3 / 1000",
        f"        = {result['TN_kg_per_yr']:.2f} kg/yr",
        f"TP Load = {data.emc_mg_per_L_TP} mg/L * {result['runoff_volume_m3']:.2f} m^3 / 1000",
        f"        = {result['TP_kg_per_yr']:.2f} kg/yr",
    ]
    return "\n".join(lines)


def save_site_data(data: SiteData, filepath: str) -> None:
    """Save site data to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(asdict(data), f, indent=2)


def load_site_data(filepath: str) -> SiteData:
    """Load site data from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return SiteData(**data)
harper_calc/cli.py
New
+64
-0

"""Command-line interface for the Harper nutrient loading calculator."""
import argparse
from .calculator import (
    SiteData,
    calculate_site_loads,
    load_site_data,
    save_site_data,
)
from .defaults import DEFAULT_EMC, RUNOFF_COEFFICIENT


def main(argv=None):
    parser = argparse.ArgumentParser(description="Harper Nutrient Loading Calculator")
    parser.add_argument("--landuse", choices=DEFAULT_EMC.keys(), default="residential", help="Land use type")
    parser.add_argument("--area", type=float, help="Site area in acres")
    parser.add_argument("--rainfall", type=float, default=1.0, help="Annual rainfall in meters")
    parser.add_argument("--emc_tn", type=float, help="Override TN EMC in mg/L")
    parser.add_argument("--emc_tp", type=float, help="Override TP EMC in mg/L")
    parser.add_argument("--runoff_coeff", type=float, help="Override runoff coefficient")
    parser.add_argument("--load", type=str, help="Load site data from JSON file")
    parser.add_argument("--save", type=str, help="Save site data to JSON file")

    args = parser.parse_args(argv)

    loaded = load_site_data(args.load) if args.load else None

    landuse = args.landuse
    emc_tn = args.emc_tn if args.emc_tn is not None else (
        loaded.emc_mg_per_L_TN if loaded else DEFAULT_EMC[landuse]["TN"]
    )
    emc_tp = args.emc_tp if args.emc_tp is not None else (
        loaded.emc_mg_per_L_TP if loaded else DEFAULT_EMC[landuse]["TP"]
    )
    runoff_coeff = args.runoff_coeff if args.runoff_coeff is not None else (
        loaded.runoff_coefficient if loaded else RUNOFF_COEFFICIENT[landuse]
    )

    area = args.area if args.area is not None else (loaded.area_acres if loaded else None)
    rainfall = args.rainfall if args.rainfall is not None else (
        loaded.annual_rainfall_m if loaded else None
    )
    if area is None:
        parser.error("--area is required if not loaded from file")

    site_data = SiteData(
        area_acres=area,
        annual_rainfall_m=rainfall,
        runoff_coefficient=runoff_coeff,
        emc_mg_per_L_TN=emc_tn,
        emc_mg_per_L_TP=emc_tp,
    )

    result = calculate_site_loads(site_data)

    print(f"Annual Runoff Volume (m^3): {result['runoff_volume_m3']:.2f}")
    print(f"Annual TN Load (kg/yr): {result['TN_kg_per_yr']:.2f}")
    print(f"Annual TP Load (kg/yr): {result['TP_kg_per_yr']:.2f}")

    if args.save:
        save_site_data(site_data, args.save)


if __name__ == "__main__":
    main()