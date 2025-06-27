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