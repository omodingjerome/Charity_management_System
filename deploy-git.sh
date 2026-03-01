#!/bin/bash
# Git Pull Deployment Script for DreamHost
# Run this on server to pull latest updates

PROJECT_DIR="/home/cms_admin1/cms.reachapac.org"
VENV_DIR="$PROJECT_DIR/venv"

cd "$PROJECT_DIR"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Pull latest from Git
git pull

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart Passenger
touch "$PROJECT_DIR/passenger_wsgi.py"

echo "Deployment complete!"
