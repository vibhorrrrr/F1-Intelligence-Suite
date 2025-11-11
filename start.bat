@echo off
echo ================================================================================
echo    F1 STRATEGY SUITE - LAUNCHER
echo ================================================================================
echo.
echo Starting F1 Strategy Intelligence Suite...
echo.
echo [1/2] Launching Landing Page on http://localhost:8051
echo [2/2] Launching Main Dashboard on http://localhost:8050
echo.
echo ================================================================================
echo.

REM Start landing page in a new window
start "F1 Landing Page - Port 8051" cmd /k "python ui/landing_page.py"

REM Wait 3 seconds before starting dashboard
timeout /t 3 /nobreak >nul

REM Start dashboard in a new window (minimized, runs in background)
start "F1 Dashboard - Port 8050" cmd /k "python ui/ultimate_dashboard.py"

REM Wait 5 seconds for servers to start
timeout /t 5 /nobreak >nul

REM Open only landing page in browser
start http://localhost:8051

echo.
echo ================================================================================
echo    SERVERS RUNNING!
echo ================================================================================
echo.
echo Landing Page:  http://localhost:8051
echo Main Dashboard: http://localhost:8050 (running in background)
echo.
echo Navigate to Dashboard from the Landing Page buttons
echo.
echo Press Ctrl+C in each window to stop the servers
echo Close this window when done
echo.
echo ================================================================================

pause
