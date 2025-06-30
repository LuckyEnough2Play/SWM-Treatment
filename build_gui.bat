@echo off
echo Building harper_gui executable...

REM Activate your virtual environment if needed
REM call venv\Scripts\activate

pyinstaller --onefile --windowed --name harper_gui harper_calc/gui.py

echo Build complete. Executable located in the dist folder.
pause
