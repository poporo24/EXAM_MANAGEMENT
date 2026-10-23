@echo off
cd /d "%~dp0"
echo ========================================================
echo   CCA Exam Management - 1-Click Server Update
echo   Server: 165.22.100.18 (cca-exam.duckdns.org)
echo ========================================================
echo.
echo [1/2] Uploading latest files to server...
echo Enter your root password when prompted:
scp cca_exam_deploy.zip root@165.22.100.18:/root/
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Upload failed. Please check your password.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Applying update, setting Philippine Timezone, and restarting app...
echo Enter your root password one more time:
ssh root@165.22.100.18 "timedatectl set-timezone Asia/Manila && unzip -o /root/cca_exam_deploy.zip -d /var/www/cca_exam/ && sed -i 's/gunicorn -w 3 -b/gunicorn -w 3 --timeout 120 -b/g' /etc/systemd/system/cca_exam.service && systemctl daemon-reload && systemctl restart cca_exam && echo. && echo [SUCCESS] Server time is now: && date"

echo.
echo ========================================================
echo   ALL DONE! Your cloud server is completely updated!
echo   Website: https://cca-exam.duckdns.org
echo ========================================================
echo.
pause
