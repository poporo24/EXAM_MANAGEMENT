@echo off
cd /d "%~dp0"
echo ========================================================
echo   CCA Exam Management - 1-Click Server Update
echo   Server: 165.22.100.18 (cca-exam.duckdns.org)
echo ========================================================
echo.
echo [1/3] Packaging latest updates into cca_exam_deploy.zip...
python -c "import zipfile, os; targets = ['app.py', 'requirements.txt', 'deploy_remote.sh', 'update_server_now.bat', 'template', 'static', 'system']; zf = zipfile.ZipFile('cca_exam_deploy.zip', 'w', zipfile.ZIP_DEFLATED); [zf.write(t, arcname=t) if os.path.isfile(t) else [zf.write(os.path.join(r, f), arcname=os.path.relpath(os.path.join(r, f), '.')) for r, d, fs in os.walk(t) if '__pycache__' not in r for f in fs if not f.endswith('.pyc')] for t in targets]; zf.close()"
echo Package ready.
echo.
echo [2/3] Uploading latest files and deploy script to server...
echo Enter your root password when prompted:
scp cca_exam_deploy.zip deploy_remote.sh root@165.22.100.18:/root/
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Upload failed. Please check your password.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Running automated server deployment...
echo Enter your root password one more time:
ssh root@165.22.100.18 "bash /root/deploy_remote.sh"

echo.
echo ========================================================
echo   ALL DONE! Your cloud server is completely updated!
echo   Website: https://cca-exam.duckdns.org
echo ========================================================
echo.
pause
