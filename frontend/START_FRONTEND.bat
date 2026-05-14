@echo off
title Binance Trading Bot - Frontend
color 0B
echo ========================================
echo    Binance Futures Trading Bot
echo    Frontend (React Dashboard)
echo ========================================
echo.
echo [1] Verificando Node.js...
node --version 2>nul
if errorlevel 1 (
    echo [ERRO] Node.js nao encontrado!
    echo.
    echo    Instale Node.js em: https://nodejs.org/en/download/
    echo    Escolha: Windows Installer (.msi)
    echo.
    echo    Apos instalar, feche e reabra este terminal.
    pause
    exit /b 1
)

echo [OK] Node.js encontrado!
npm --version

echo [2] Instalando dependencias (primeira vez only)...
if not exist "node_modules" (
    echo    Instalando pacotes... (aguarde)
    npm install
    echo [OK] Dependencias instaladas!
) else (
    echo [OK] Dependencias ja instaladas.
)

echo [3] Iniciando servidor de desenvolvimento...
echo.
echo    ===========================================
echo    Frontend rodando:
echo      Dashboard: http://localhost:5173
echo    ===========================================
echo.
echo    Pressione CTRL+C para parar
echo    ===========================================
echo.

npm run dev

echo.
echo [INFO] Servidor frontend encerrado.
pause
