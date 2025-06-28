"""Calculation utilities for the Harper nutrient loading tool."""
from dataclasses import dataclass, asdict
import json

# Simple citations used in breakdowns and reports
CITATIONS = {
    "runoff": "Harper 2007 Eq.3-1",
    "emc": "Harper 2007 Table 4-4",
}


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
    tn_kg = calculate_annual_load(data.emc_mg_per_L_TN, runoff_volume)
    tp_kg = calculate_annual_load(data.emc_mg_per_L_TP, runoff_volume)
    # convenience results in pounds/year
    tn_lb = tn_kg * 2.20462
    tp_lb = tp_kg * 2.20462
    return {
        "TN_kg_per_yr": tn_kg,
        "TP_kg_per_yr": tp_kg,
        "TN_lb_per_yr": tn_lb,
        "TP_lb_per_yr": tp_lb,
        "runoff_volume_m3": runoff_volume,
    }


def format_breakdown(data: SiteData, result: dict) -> str:
    """Return a multiline string showing calculation steps."""
    area_m2 = data.area_acres * 4046.8564224
    lines = [
        "Calculation Breakdown:",
        f"Runoff Volume = {data.area_acres} ac * 4046.8564224 m^2/ac = {area_m2:.2f} m^2",
        f"               * {data.annual_rainfall_m} m * {data.runoff_coefficient} ({CITATIONS['runoff']})",
        f"               = {result['runoff_volume_m3']:.2f} m^3",
        f"TN Load = {data.emc_mg_per_L_TN} mg/L * {result['runoff_volume_m3']:.2f} m^3 / 1000 ({CITATIONS['emc']})",
        f"        = {result['TN_kg_per_yr']:.2f} kg/yr ({result['TN_lb_per_yr']:.2f} lb/yr)",
        f"TP Load = {data.emc_mg_per_L_TP} mg/L * {result['runoff_volume_m3']:.2f} m^3 / 1000 ({CITATIONS['emc']})",
        f"        = {result['TP_kg_per_yr']:.2f} kg/yr ({result['TP_lb_per_yr']:.2f} lb/yr)",
        "",
        "References:",
        "Harper, H. H., et al. 2007. Florida Stormwater Treatment Manual.",
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
