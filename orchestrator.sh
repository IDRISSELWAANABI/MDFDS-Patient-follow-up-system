#!/bin/bash

# Define the project directory
PROJECT_DIR="$HOME/Desktop/test/MDFDS-Patient-follow-up-system"

# Function to perform all the steps
setup_and_run() {
    echo "Navigating to project directory..."
    cd "$PROJECT_DIR" || { echo "Failed to navigate to project directory"; exit 1; }

    echo "Removing old virtual environment if it exists..."
    rm -rf .venv

    echo "Creating virtual environment..."
    python3 -m venv .venv || return 1

    echo "Activating virtual environment..."
    source .venv/bin/activate || return 1

    echo "Installing requirements..."
    pip3 install -r ./requirements.txt || return 1

    echo "Starting Streamlit app..."
    streamlit run app.py || return 1
}

# Infinite loop until successful
while true; do
    setup_and_run
    if [ $? -eq 0 ]; then
        echo "Application ran successfully!"
        break
    else
        echo "An error occurred. Retrying after a short pause..."
        sleep 3
    fi
done
