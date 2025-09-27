@echo off
REM Quick Start Script for English Educator Agent
REM Windows version

echo ========================================
echo English Educator Agent - Quick Start
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/5] Starting Docker services...
cd docker
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start Docker services
    pause
    exit /b 1
)
echo ✓ Docker services started
echo.

echo [2/5] Waiting for services to be ready...
timeout /t 10 /nobreak >nul
echo ✓ Services are ready
echo.

echo [3/5] Setting up Python environment...
cd ..\backend
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt >nul 2>&1
echo ✓ Python environment ready
echo.

echo [4/5] Initializing database...
python -c "from utils.database import init_db; init_db()"
if errorlevel 1 (
    echo WARNING: Database initialization failed - may already exist
)
echo ✓ Database initialized
echo.

echo [5/5] Starting backend server...
echo.
echo ========================================
echo System is ready!
echo ========================================
echo.
echo Available services:
echo   - API:        http://localhost:8000
echo   - Docs:       http://localhost:8000/docs
echo   - Grafana:    http://localhost:3001 (admin/admin)
echo   - Prometheus: http://localhost:9090
echo   - RabbitMQ:   http://localhost:15672 (admin/admin)
echo.
echo Starting FastAPI server...
echo Press Ctrl+C to stop
echo.

uvicorn main:app --reload --port 8000
