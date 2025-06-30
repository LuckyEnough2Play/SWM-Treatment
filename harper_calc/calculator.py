"""Calculation utilities for the Harper nutrient loading tool."""
from dataclasses import dataclass, asdict
import json

# Simple citations used in breakdowns and reports
CITATIONS = {
    "runoff": "Harper 2007 Eq.3-1",
    "emc": "Harper 2007 Table 4-4",
}

# Default nutrient removal efficiencies for common treatment practices
# Values approximate those presented in Harper report tables.
TREATMENT_EFFICIENCY = {
    "dry_detention_filtration": {"TN": 0.30, "TP": 0.40},
    "off_line_retention_detention": {"TN": 0.65, "TP": 0.80},
    "infiltration": {"TN": 1.0, "TP": 1.0},
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


def save_subareas(subareas: list[SiteData], filepath: str) -> None:
    """Save a list of subareas to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([asdict(sa) for sa in subareas], f, indent=2)


def load_subareas(filepath: str) -> list[SiteData]:
    """Load a list of subareas from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [SiteData(**d) for d in data]


def aggregate_site_loads(subareas: list[SiteData]) -> dict:
    """Aggregate loads for multiple subareas."""
    total_volume = 0.0
    total_tn = 0.0
    total_tp = 0.0
    for sa in subareas:
        vol = calculate_runoff_volume(sa.area_acres, sa.annual_rainfall_m, sa.runoff_coefficient)
        total_volume += vol
        total_tn += calculate_annual_load(sa.emc_mg_per_L_TN, vol)
        total_tp += calculate_annual_load(sa.emc_mg_per_L_TP, vol)
    return {
        "TN_kg_per_yr": total_tn,
        "TP_kg_per_yr": total_tp,
        "TN_lb_per_yr": total_tn * 2.20462,
        "TP_lb_per_yr": total_tp * 2.20462,
        "runoff_volume_m3": total_volume,
    }


def compare_scenarios(pre: list[SiteData], post: list[SiteData]) -> dict:
    """Compare pre- and post-development scenarios for no net increase."""
    pre_result = aggregate_site_loads(pre)
    post_result = aggregate_site_loads(post)
    return {
        "pre": pre_result,
        "post": post_result,
        "tn_no_increase": post_result["TN_kg_per_yr"] <= pre_result["TN_kg_per_yr"],
        "tp_no_increase": post_result["TP_kg_per_yr"] <= pre_result["TP_kg_per_yr"],
    }


def apply_treatment(loads: dict, treatment: str) -> dict:
    """Apply a treatment efficiency to the calculated loads."""
    eff = TREATMENT_EFFICIENCY.get(treatment)
    if eff is None:
        raise ValueError(f"Unknown treatment: {treatment}")
    tn = loads["TN_kg_per_yr"] * (1 - eff["TN"])
    tp = loads["TP_kg_per_yr"] * (1 - eff["TP"])
    return {
        "TN_kg_per_yr": tn,
        "TP_kg_per_yr": tp,
        "TN_lb_per_yr": tn * 2.20462,
        "TP_lb_per_yr": tp * 2.20462,
        "runoff_volume_m3": loads["runoff_volume_m3"],
    }
