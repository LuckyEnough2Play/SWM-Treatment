"""Calculation utilities for the Harper nutrient loading tool."""
from dataclasses import dataclass


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
