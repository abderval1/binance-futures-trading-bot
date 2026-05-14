#!/bin/bash
echo "========================================"
echo "Binance Futures Trading Bot - Start"
echo "========================================"
echo ""

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting backend server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
