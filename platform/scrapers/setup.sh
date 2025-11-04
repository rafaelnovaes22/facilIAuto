#!/bin/bash
# Setup script for RobustCar Scraper (Linux/Mac)

echo "========================================"
echo "RobustCar Scraper - Setup"
echo "========================================"
echo ""

echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Setup completed successfully!"
    echo "========================================"
    echo ""
    echo "You can now run the scraper:"
    echo "  python -m scraper.orchestrator --mode full"
    echo ""
else
    echo ""
    echo "========================================"
    echo "Setup failed! Please check the errors above."
    echo "========================================"
    echo ""
    exit 1
fi
