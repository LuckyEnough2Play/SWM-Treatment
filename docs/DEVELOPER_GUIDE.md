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
Create standalone executables with **PyInstaller**. Install it first:

```bash
pip install pyinstaller
```

### Command line tool

Build the CLI for each platform:

```bash
# Linux
pyinstaller --onefile --name harper_calc harper_calc/cli.py

# Windows
pyinstaller --onefile --name harper_calc.exe harper_calc/cli.py
```

### Graphical interface

Use the same approach for the GUI application:

```bash
# Linux
pyinstaller --windowed --onefile --name harper_gui harper_calc/gui.py

# Windows
pyinstaller --windowed --onefile --name harper_gui.exe harper_calc/gui.py
```

If the Windows build fails with a `PermissionError` on `harper_gui.exe`, ensure no prior copy of the file is running or locked. Removing the old executable from `dist/` before rerunning PyInstaller usually resolves the issue.

The resulting executables will appear in the `dist/` directory. Copy the appropriate binary to users as needed.