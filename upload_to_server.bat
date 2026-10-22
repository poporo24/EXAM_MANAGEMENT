@echo off
cd /d "%~dp0"
echo ========================================================
echo   Uploading Exam Management Project to DigitalOcean
echo   Server: 165.22.100.18
echo ========================================================
echo.
echo When prompted, enter your Droplet root password:
echo (Note: characters will not show while typing password)
echo.
scp cca_exam_deploy.zip root@165.22.100.18:/root/
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Upload completed successfully!
) else (
    echo [ERROR] Upload failed. Please check your password.
)
pause
