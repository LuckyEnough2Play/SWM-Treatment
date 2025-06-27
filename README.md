# Harper Report-Based Nutrient Loading Calculator

This repository contains a prototype implementation of the Harper nutrient loading calculator described in `harper_nutrient_calculator_prd.txt`.

## Features
- Core formulas to compute annual runoff volume and nutrient loads
- Sample default EMC and runoff coefficient values
- Command-line interface for quick calculations
- Basic unit tests

## Running the GUI
```bash
python -m harper_calc.gui
```

## Running the CLI
```bash
python -m harper_calc.cli --area 2.5 --landuse residential --rainfall 1.2
```

## Running Tests
```bash
pytest
```
