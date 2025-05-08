#!/bin/bash

# Deployment script for SPOTLAWFUL AI API server

echo "Starting deployment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Export environment variables if any (example)
# export FLASK_ENV=production

# Run database migrations if applicable
# flask db upgrade

# Start the API server with Gunicorn for production
gunicorn -w 4 -b 0.0.0.0:8000 spotlawful_ai.api_server:app

echo "Deployment completed and server started on port 8000."
