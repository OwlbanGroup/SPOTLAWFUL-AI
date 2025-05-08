@echo off
REM Deployment script for SPOTLAWFUL AI backend on Windows

echo Starting deployment...

REM Create virtual environment if not exists
if not exist venv (
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM Run tests
echo Running tests...
pytest spotlawful_ai\test_api_server.py
if errorlevel 1 (
    echo Tests failed. Aborting deployment.
    exit /b 1
)

REM Start the API server with Waitress
echo Starting API server...
start /b waitress-serve --host=0.0.0.0 --port=5000 spotlawful_ai.api_server:app

echo Deployment completed.
