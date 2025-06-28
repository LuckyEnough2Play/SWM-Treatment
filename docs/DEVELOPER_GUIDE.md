# Developer Guide

This project is a prototype for calculating stormwater nutrient loads.

## Setup
1. Install dependencies:
   ```bash
   pip install -e .
   ```
2. Run tests:
   ```bash
   pytest -q
   ```

## Repository Layout
- `harper_calc/` – Calculator package
- `tests/` – Unit tests
- `docs/` – User and developer guides
- `Task_History.md` – Progress tracker

## Contribution Tips
- Follow PEP 8 style conventions.
- Add tests for new features.
- Update `Task_History.md` when tasks change status.

## Packaging
To create a standalone executable for distribution, the project can be packaged
with PyInstaller.

```bash
pip install pyinstaller
pyinstaller --onefile -n harper_calc harper_calc/cli.py
```

The resulting executable is placed in the `dist/` directory. Run PyInstaller on
each target platform (e.g., Windows or Linux) to build native binaries.
