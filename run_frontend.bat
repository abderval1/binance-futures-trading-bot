@echo off
cd /d "%~dp0.."
echo ========================================
echo Binance Futures Bot - Frontend
echo ========================================
echo.
echo Frontend starting on http://localhost:5173
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

cd frontend
call npm run dev
