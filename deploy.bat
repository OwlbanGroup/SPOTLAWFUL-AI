@echo off
REM Deployment script for SPOTLAWFUL AI API server on Windows

echo Starting deployment...

REM Create virtual environment if not exists
if not exist venv (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install required packages including Flask, Waitress, and spaCy
pip install flask
pip install waitress
pip install spacy

REM Run the API server with Waitress for production
call venv\Scripts\waitress-serve.exe --listen=*:8000 spotlawful_ai.api_server:app

echo Deployment completed and server started on port 8000.
