@echo off
setlocal
cd /d "%~dp0"

:: Check if python is in PATH
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python app.py
    goto end
)

:: Fallback to default Python 3.12 install location
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" app.py
    goto end
)

echo Python executable not found. Please restart your terminal or restart your computer to apply the PATH changes.
pause

:end
endlocal
