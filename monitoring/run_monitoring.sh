#!/bin/bash

# Ensure we are in the right directory
set -e
cd "$(dirname "$0")/.."

echo "Installing dependencies..."
python -m pip install -r monitoring/requirements.txt

echo "Preparing data..."
python monitoring/prepare_data.py

echo "Generating report..."
python monitoring/generate_report.py

echo "Done! Report saved to monitoring_report.html"
