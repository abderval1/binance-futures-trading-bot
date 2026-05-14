@echo off
title Binance Futures Trading Bot - Backend
color 0A
echo ========================================
echo    Binance Futures Trading Bot
echo    Backend Server
echo ========================================
echo.
echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [INFO] Verificando dependencias...
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo [ERRO] Dependencias nao instaladas!
    echo Execute: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [OK] Ambiente pronto.
echo.
echo [INFO] Iniciando servidor...
echo       URL: http://0.0.0.0:8000
echo       Docs: http://localhost:8000/docs
echo       Health: http://localhost:8000/health
echo.
echo ========================================
echo Pressione CTRL+C para parar o servidor
echo ========================================
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo.
echo [INFO] Servidor encerrado.
pause
