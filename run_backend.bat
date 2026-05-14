@echo off
cd /d "%~dp0.."
echo ========================================
echo Binance Futures Trading Bot
echo ========================================
echo.
echo Backend starting on http://0.0.0.0:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

cd backend
call .\venv\Scripts\activate.bat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
