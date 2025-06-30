# User Guide

This guide explains how to use the Harper Nutrient Loading Calculator.

## GUI
1. Launch the GUI:
   ```bash
   python -m harper_calc.gui
   ```
2. Enter the **Area** of the site in acres.
3. Choose the **Land Use** and adjust defaults if needed:
   - **Runoff Coefficient**
   - **EMC TN (mg/L)**
   - **EMC TP (mg/L)**
4. Click **Calculate** to see results and formula details.
5. Use **Export PDF** to save a report.
6. The **File** menu lets you **Open** or **Save** scenario files.
7. Select **Help > About** for a quick method overview.

## CLI
Run the calculator from the command line:
```bash
python -m harper_calc.cli --landuse residential --area 2.5 --rainfall 1.2
```
Optional flags allow overriding defaults or loading/saving JSON scenarios. To
aggregate multiple subareas provide a JSON file:
```bash
python -m harper_calc.cli --subareas subareas.json
```
To compare pre- and post-development scenarios:
```bash
python -m harper_calc.cli --pre pre.json --post post.json
```
To evaluate treatment performance:
```bash
python -m harper_calc.cli --area 1.0 --treatment dry_detention_filtration
```

## Method Overview
Runoff volume is calculated as:
```
area (acres) × 4046.8564224 (m²/ac) × rainfall (m) × runoff coefficient
```
Loads are:
```
EMC (mg/L) × runoff volume (m³) / 1000
```
Values are based on the 2007 Harper report.
