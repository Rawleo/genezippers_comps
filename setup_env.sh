#!/bin/bash

# Script to create and setup Python virtual environment for genezippers_comps

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Name of the virtual environment
VENV_NAME="venv"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Python virtual environment for genezippers_comps...${NC}"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Display Python version
PYTHON_VERSION=$(python3 --version)
echo -e "${YELLOW}Using: $PYTHON_VERSION${NC}"

# Create virtual environment if it doesn't exist
if [ -d "$SCRIPT_DIR/$VENV_NAME" ]; then
    echo -e "${YELLOW}Virtual environment '$VENV_NAME' already exists.${NC}"
    read -p "Do you want to remove it and create a new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Removing existing virtual environment...${NC}"
        rm -rf "$SCRIPT_DIR/$VENV_NAME"
    else
        echo -e "${YELLOW}Using existing virtual environment.${NC}"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/$VENV_NAME" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv "$SCRIPT_DIR/$VENV_NAME"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment.${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source "$SCRIPT_DIR/$VENV_NAME/bin/activate"

# Upgrade pip
echo -e "${GREEN}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo -e "${GREEN}Installing requirements from requirements.txt...${NC}"
    pip install -r "$SCRIPT_DIR/requirements.txt"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Environment setup complete!${NC}"
        echo -e "${YELLOW}To activate the environment in the future, run:${NC}"
        echo -e "${YELLOW}  source $SCRIPT_DIR/$VENV_NAME/bin/activate${NC}"
    else
        echo -e "${RED}Error: Failed to install requirements.${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: requirements.txt not found in $SCRIPT_DIR${NC}"
    exit 1
fi
