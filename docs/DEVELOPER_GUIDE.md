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
- The CLI now supports multi-catchment files via `--subareas` and
  scenario comparison via `--pre`/`--post`. Unit tests should cover
  these options.
- Treatment effects can be applied with the `--treatment` option.
- Update `Task_History.md` when tasks change status.

See [SUPPORT_PLAN.md](SUPPORT_PLAN.md) for issue reporting and release
policies.

## Packaging
To create standalone executables for distribution, build the project with
PyInstaller on each target platform.

Install PyInstaller:

```bash
pip install pyinstaller
```

Build for Linux:

```bash
pyinstaller --onefile --name harper_calc harper_calc/cli.py
```

Build for Windows (run in a Windows environment):

```bash
pyinstaller --onefile --name harper_calc.exe harper_calc/cli.py
```

The resulting executables are located in the `dist/` directory of the build
machine. Copy the appropriate binary to users as needed.