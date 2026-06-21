#!/bin/bash
# Startup script for RAG-Enhanced Workflow Optimization Web Interface

echo "Starting RAG-Enhanced Workflow Optimization System Web Interface..."
echo "=================================================================="

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Installing required dependencies..."
    pip3 install -r ../requirements.txt
fi

# Set environment variables if .env exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    source .env
fi

# Launch streamlit application
echo "Launching web interface on http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run ../web_interface.py --server.port 8501 --server.headless false --browser.gatherUsageStats false