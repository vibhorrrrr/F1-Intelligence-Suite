@echo off
echo ================================================================================
echo    F1 STRATEGY SUITE - SHUTDOWN
echo ================================================================================
echo.
echo Stopping all F1 Strategy Suite servers...
echo.

REM Kill processes on port 8051 (Landing Page)
echo [1/2] Stopping Landing Page (Port 8051)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8051') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill processes on port 8050 (Dashboard)
echo [2/2] Stopping Dashboard (Port 8050)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8050') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ================================================================================
echo    ALL SERVERS STOPPED!
echo ================================================================================
echo.
echo Ports 8050 and 8051 are now free
echo.

pause
