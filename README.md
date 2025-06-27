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
- Built-in help window and separate user/developer guides

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

## Running Tests
```bash
pytest
```
