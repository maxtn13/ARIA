@echo off
echo.
echo   ARIA -- Autonomous Resident Intelligence Assistant
echo   --------------------------------------------------
echo.
echo   Setting up...

python -m venv .venv
call .venv\Scripts\activate.bat

pip install PyQt6 psutil --quiet

echo.
echo   Launching ARIA...
echo   (Look for the ARIA icon in your system tray)
echo   (Press Ctrl+Space anywhere to open/close ARIA)
echo.
python aria.py
pause
