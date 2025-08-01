@echo off
echo ========================================
echo    WAF System Startup Script
echo ========================================
echo.

echo [1/4] Starting MongoDB (if not running)...
echo Note: Make sure MongoDB is installed and running
echo You can start it with: mongod
echo.

echo [2/4] Starting Flask API Server...
echo Starting on http://localhost:5000
start "Flask API" cmd /k "python api_server.py"
timeout /t 3 /nobreak >nul

echo [3/4] Starting React Frontend...
echo Starting on http://localhost:3000
start "React Frontend" cmd /k "npm start"
timeout /t 5 /nobreak >nul

echo [4/4] Starting mitmproxy (optional)...
echo To start mitmproxy manually, run:
echo mitmdump -s proxy/waf_proxy.py -p 8082
echo.
echo Then configure your browser to use proxy:
echo Address: 127.0.0.1
echo Port: 8082
echo.

echo ========================================
echo    Services Started!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo API: http://localhost:5000
echo.
echo Press any key to exit...
pause >nul 