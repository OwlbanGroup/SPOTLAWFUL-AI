@echo off
REM Deployment script for SPOTLAWFUL AI API server on Windows

echo Starting deployment...

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM Run the API server with Waitress for production
REM Install Waitress if not installed: pip install waitress
waitress-serve --listen=*:8000 spotlawful_ai.api_server:app

echo Deployment completed and server started on port 8000.
