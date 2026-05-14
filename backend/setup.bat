@echo off
echo ==========================================
echo Binance Futures Bot - Windows Setup
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from python.org
    pause
    exit /b 1
)

REM Check PostgreSQL
echo Note: PostgreSQL must be installed manually from postgresql.org
echo.

cd backend

REM Create virtualenv
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist .env (
    echo.
    echo =========================================
    echo Creating .env from template...
    echo =========================================
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env and add your values:
    echo   1. DATABASE_URL=postgresql://...
    echo   2. SECRET_KEY= (generate with Python)
    echo   3. ENCRYPTION_KEY= (32 byte hex)
    echo   4. BINANCE_API_KEY= (your key)
    echo   5. BINANCE_SECRET_KEY= (your secret)
    echo.
    pause
)

REM Initialize database
echo Initializing database...
python setup.py

echo.
echo =========================================
echo Setup complete!
echo =========================================
echo.
echo Next: Start frontend
echo   1. Open new terminal
echo   2. cd frontend
echo   3. npm install
echo   4. npm run dev
echo.
echo Or start backend with:
echo   uvicorn app.main:app --reload --port 8000
echo.
pause
