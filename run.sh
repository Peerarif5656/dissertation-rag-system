#!/bin/bash
# Run script for RAG-Enhanced Workflow Optimization System

echo " Starting Workflow Optimization System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r ../requirements.txt

# Set default environment variables if not set
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-eu-west-2}
export DATA_DIRECTORY=${DATA_DIRECTORY:-.}

echo " System Configuration:"
echo "   AWS Region: $AWS_DEFAULT_REGION"  
echo "   Data Directory: $DATA_DIRECTORY"
echo "   AWS Credentials: $([ -n "$AWS_ACCESS_KEY_ID" ] && echo "Configured" || echo "Not configured")"

# Run the application
echo " Starting web interface..."
streamlit run ../web_interface.py --server.port 8501
