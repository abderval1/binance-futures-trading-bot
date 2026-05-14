@echo off
cd /d "%~dp0.."
echo Starting Binance Futures Trading Bot...
echo.
echo Backend will run on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
call backend\venv\Scripts\activate.bat
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
