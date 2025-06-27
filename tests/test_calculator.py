"""Tests for the calculation utilities."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harper_calc.calculator import calculate_annual_load, calculate_runoff_volume


def test_calculate_runoff_volume():
    vol = calculate_runoff_volume(area_acres=1.0, annual_rainfall_m=1.0, runoff_coefficient=0.5)
    # 1 acre = 4046.8564224 m^2, so volume = 4046.8564224 * 1 * 0.5
    assert abs(vol - 2023.4282112) < 1e-6


def test_calculate_annual_load():
    load = calculate_annual_load(2.0, 1000.0)
    # 2 mg/L * 1000 m^3 => 2 * 1000 / 1000 = 2 kg
    assert abs(load - 2.0) < 1e-6
