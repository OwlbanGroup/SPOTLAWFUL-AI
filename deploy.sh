#!/bin/bash

# Deployment script for SPOTLAWFUL AI backend

echo "Starting deployment..."

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
  python -m venv venv
  echo "Virtual environment created."
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run tests
echo "Running tests..."
pytest spotlawful_ai/test_api_server.py
if [ $? -ne 0 ]; then
  echo "Tests failed. Aborting deployment."
  exit 1
fi

# Start the API server with Waitress
echo "Starting API server..."
nohup waitress-serve --host=0.0.0.0 --port=5000 spotlawful_ai.api_server:app &

echo "Deployment completed."
