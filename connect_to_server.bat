@echo off
cd /d "%~dp0"
echo ========================================================
echo   Connecting to CCA Exam Cloud Server (165.22.100.18)
echo ========================================================
echo.
echo When prompted, enter your root password:
echo (Note: characters will NOT show while typing password)
echo.
ssh root@165.22.100.18
pause
