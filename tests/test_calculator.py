"""Tests for the calculation utilities."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harper_calc.calculator import (
    calculate_annual_load,
    calculate_runoff_volume,
    SiteData,
    calculate_site_loads,
    format_breakdown,
    save_site_data,
    load_site_data,
)


def test_calculate_runoff_volume():
    vol = calculate_runoff_volume(area_acres=1.0, annual_rainfall_m=1.0, runoff_coefficient=0.5)
    # 1 acre = 4046.8564224 m^2, so volume = 4046.8564224 * 1 * 0.5
    assert abs(vol - 2023.4282112) < 1e-6


def test_calculate_annual_load():
    load = calculate_annual_load(2.0, 1000.0)
    # 2 mg/L * 1000 m^3 => 2 * 1000 / 1000 = 2 kg
    assert abs(load - 2.0) < 1e-6


def test_format_breakdown():
    data = SiteData(
        area_acres=1.0,
        annual_rainfall_m=1.0,
        runoff_coefficient=0.5,
        emc_mg_per_L_TN=2.0,
        emc_mg_per_L_TP=0.5,
    )
    result = calculate_site_loads(data)
    text = format_breakdown(data, result)
    assert "Runoff Volume" in text and "TN Load" in text


def test_save_load(tmp_path):
    data = SiteData(1.0, 1.0, 0.5, 2.0, 0.5)
    f = tmp_path / "site.json"
    save_site_data(data, f)
    loaded = load_site_data(f)
    assert loaded == data