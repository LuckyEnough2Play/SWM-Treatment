import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harper_calc import cli
from harper_calc.calculator import SiteData, save_subareas

def test_cli_basic(capsys):
    cli.main(["--landuse", "residential", "--area", "1.0", "--rainfall", "39.37", "--runoff_coeff", "0.5", "--emc_tn", "2.0", "--emc_tp", "0.5"])
    out = capsys.readouterr().out
    assert "Annual Runoff Volume" in out
    assert "Annual TN Load" in out

def test_cli_save_load(tmp_path, capsys):
    json_file = tmp_path / "site.json"
    cli.main(["--landuse", "residential", "--area", "1.0", "--rainfall", "39.37", "--save", str(json_file)])
    assert json_file.exists()
    cli.main(["--load", str(json_file)])
    out = capsys.readouterr().out
    assert "Annual Runoff Volume" in out


def test_cli_subareas(tmp_path, capsys):
    data = [
        {
            "area_acres": 1.0,
            "annual_rainfall_m": 1.0,
            "runoff_coefficient": 0.5,
            "emc_mg_per_L_TN": 2.0,
            "emc_mg_per_L_TP": 0.5,
        },
        {
            "area_acres": 1.5,
            "annual_rainfall_m": 1.0,
            "runoff_coefficient": 0.4,
            "emc_mg_per_L_TN": 1.8,
            "emc_mg_per_L_TP": 0.4,
        },
    ]
    f = tmp_path / "subs.json"
    save_subareas([SiteData(**d) for d in data], f)
    cli.main(["--subareas", str(f)])
    out = capsys.readouterr().out
    assert "Annual TN Load" in out


def test_cli_treatment(capsys):
    cli.main([
        "--landuse",
        "residential",
        "--area",
        "1.0",
        "--treatment",
        "infiltration",
    ])
    out = capsys.readouterr().out
    assert "Treated TN Load" in out


def test_cli_compare(tmp_path, capsys):
    pre = [SiteData(1.0, 1.0, 0.5, 2.0, 0.5)]
    post = [SiteData(1.0, 1.0, 0.4, 1.8, 0.4)]
    pre_file = tmp_path / "pre.json"
    post_file = tmp_path / "post.json"
    save_subareas(pre, pre_file)
    save_subareas(post, post_file)
    cli.main(["--pre", str(pre_file), "--post", str(post_file)])
    out = capsys.readouterr().out
    assert "No net increase" in out


def test_cli_compare_treated(tmp_path, capsys):
    pre = [SiteData(1.0, 1.0, 0.5, 2.0, 0.5)]
    post = [SiteData(1.0, 1.0, 0.4, 1.8, 0.4)]
    pre_file = tmp_path / "pre.json"
    post_file = tmp_path / "post.json"
    save_subareas(pre, pre_file)
    save_subareas(post, post_file)
    cli.main(["--pre", str(pre_file), "--post", str(post_file), "--treatment", "dry_detention_filtration"])
    out = capsys.readouterr().out
    assert "No net increase" in out

