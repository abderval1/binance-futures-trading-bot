@echo off
echo ========================================
echo Binance Futures Trading Bot - Start
echo ========================================
echo.

REM Check if virtualenv exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt > nul

echo Starting backend server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
