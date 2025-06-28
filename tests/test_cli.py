import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harper_calc import cli
from harper_calc.calculator import SiteData

def test_cli_basic(capsys):
    cli.main(["--landuse", "residential", "--area", "1.0", "--rainfall", "1.0", "--runoff_coeff", "0.5", "--emc_tn", "2.0", "--emc_tp", "0.5"])
    out = capsys.readouterr().out
    assert "Annual Runoff Volume" in out
    assert "Annual TN Load" in out

def test_cli_save_load(tmp_path, capsys):
    json_file = tmp_path / "site.json"
    cli.main(["--landuse", "residential", "--area", "1.0", "--rainfall", "1.0", "--save", str(json_file)])
    assert json_file.exists()
    cli.main(["--load", str(json_file)])
    out = capsys.readouterr().out
    assert "Annual Runoff Volume" in out
