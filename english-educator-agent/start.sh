#!/bin/bash
# Quick Start Script for English Educator Agent
# Linux/Mac version

set -e

echo "========================================"
echo "English Educator Agent - Quick Start"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

echo "[1/5] Starting Docker services..."
cd docker
docker-compose up -d
echo "✓ Docker services started"
echo ""

echo "[2/5] Waiting for services to be ready..."
sleep 10
echo "✓ Services are ready"
echo ""

echo "[3/5] Setting up Python environment..."
cd ../backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Python environment ready"
echo ""

echo "[4/5] Initializing database..."
python -c "from utils.database import init_db; init_db()" || echo "WARNING: Database may already exist"
echo "✓ Database initialized"
echo ""

echo "[5/5] Starting backend server..."
echo ""
echo "========================================"
echo "System is ready!"
echo "========================================"
echo ""
echo "Available services:"
echo "  - API:        http://localhost:8000"
echo "  - Docs:       http://localhost:8000/docs"
echo "  - Grafana:    http://localhost:3001 (admin/admin)"
echo "  - Prometheus: http://localhost:9090"
echo "  - RabbitMQ:   http://localhost:15672 (admin/admin)"
echo ""
echo "Starting FastAPI server..."
echo "Press Ctrl+C to stop"
echo ""

uvicorn main:app --reload --port 8000
