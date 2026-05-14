@echo off
title Binance Trading Bot - Backend
color 0A
echo ========================================
echo    Binance Futures Trading Bot
echo    Backend Server
echo ========================================
echo.
echo [1] Ativando virtual environment...
call venv\Scripts\activate.bat

echo [2] Verificando Python...
python --version
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    pause
    exit /b 1
)

echo [3] Iniciando servidor FastAPI...
echo.
echo    ===========================================
echo    Servidor rodando:
echo      API: http://0.0.0.0:8000
echo      Docs: http://localhost:8000/docs
echo      Test: http://localhost:8000/health
echo    ===========================================
echo.
echo    Pressione CTRL+C para parar
echo    ===========================================
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo.
echo [INFO] Servidor encerrado.
pause
