#!/usr/bin/env python3
"""
Start script - Inicia o servidor e mantém rodando
"""
import subprocess
import sys
import time
import os

def main():
    print("=" * 60)
    print("  Binance Futures Trading Bot - Backend")
    print("=" * 60)
    print()
    print("Iniciando servidor...")
    print("  URL: http://0.0.0.0:8000")
    print("  Docs: http://localhost:8000/docs")
    print("  Health: http://localhost:8000/health")
    print()
    print("Pression CTRL+C para parar")
    print("=" * 60)
    print()

    # Mudar para diretório do backend
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Comando para iniciar uvicorn
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

    try:
        # Iniciar processo
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        print("[INFO] Servidor iniciado. Aguardando logs...")
        print()

        # Ler output em tempo real
        for line in process.stdout:
            print(line, end='', flush=True)

        process.wait()
        print(f"\n[INFO] Servidor encerrado com código {process.returncode}")

    except KeyboardInterrupt:
        print("\n[INFO] Encerrando...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
