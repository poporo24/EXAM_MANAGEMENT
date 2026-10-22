@echo off
cd /d "%~dp0"
echo ========================================================
echo   Starting Cloudflare Public Tunnel on port 9999
echo ========================================================
echo.
echo Make sure your Flask app (run.bat) is running!
echo Look below for your public URL ending in .trycloudflare.com
echo.
.\cloudflared.exe tunnel --url http://localhost:9999
pause
