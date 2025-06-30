# Harper Report-Based Nutrient Loading Calculator

This repository contains a prototype implementation of the Harper nutrient loading calculator described in `harper_nutrient_calculator_prd.txt`.

## Features
- Core formulas to compute annual runoff volume and nutrient loads
- Sample default EMC and runoff coefficient values
- Command-line interface for quick calculations
- Basic unit tests
- Simple PDF export of calculation results
- Calculation breakdown showing formulas in the GUI and exported PDF
- Save and load site scenarios as JSON
- Aggregate results for multiple subareas
- Compare pre- and post-development scenarios for no net increase
- Built-in help window and separate user/developer guides
- Apply treatment removal efficiencies to evaluate BMP performance

## Running the GUI
```bash
python -m harper_calc.gui
```
Within the GUI, calculate results and click "Export PDF" to save them.
Use the **File** menu to open or save scenario files.
Open **Help > About** for a summary of the calculation method.

See [docs/USER_GUIDE.md](docs/USER_GUIDE.md) for a full guide and
[docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for developer information.

## Running the CLI
```bash
python -m harper_calc.cli --area 2.5 --landuse residential --rainfall 1.2
```
To load or save scenarios:
```bash
python -m harper_calc.cli --load example.json
python -m harper_calc.cli --area 1.0 --save myscenario.json
```
To aggregate multiple subareas:
```bash
python -m harper_calc.cli --subareas subareas.json
```
To compare pre- and post-development scenarios:
```bash
python -m harper_calc.cli --pre pre.json --post post.json
```
To apply a treatment type when calculating loads:
```bash
python -m harper_calc.cli --area 1.0 --treatment infiltration
```

## Running Tests
```bash
pytest
```

## Packaging
Standalone executables can be created with PyInstaller. See the
[developer guide](docs/DEVELOPER_GUIDE.md#packaging) for detailed steps.

## Support
For issue reporting and maintenance policies, see
[docs/SUPPORT_PLAN.md](docs/SUPPORT_PLAN.md).

## Harper Tables
All tables extracted from the Harper Stormwater Treatment Report are organized in the `harper_tables/` directory. Each Markdown file contains the raw text for an individual table or table continuation.
