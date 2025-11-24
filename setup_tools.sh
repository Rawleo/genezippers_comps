#!/bin/bash

# Script to download bigBedToBed from UCSC into the tools directory

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOLS_DIR="$SCRIPT_DIR/tools"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}Setting up tools...${NC}"
echo -e "${BLUE}=========================================${NC}"

# Create tools directory if it doesn't exist
if [ ! -d "$TOOLS_DIR" ]; then
    echo -e "${GREEN}Creating tools directory...${NC}"
    mkdir -p "$TOOLS_DIR"
fi

cd "$TOOLS_DIR"

# =============================================
# Download bigBedToBed from UCSC
# =============================================
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Downloading bigBedToBed...${NC}"
echo -e "${BLUE}=========================================${NC}"

UCSC_BIN_DIR="$TOOLS_DIR/ucsc_bin"

if [ -f "$UCSC_BIN_DIR/bigBedToBed" ]; then
    echo -e "${YELLOW}bigBedToBed already exists.${NC}"
    read -p "Do you want to redownload? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Removing existing bigBedToBed...${NC}"
        rm -f "$UCSC_BIN_DIR/bigBedToBed"
    else
        echo -e "${YELLOW}Skipping bigBedToBed download.${NC}"
        SKIP_BIGBED=true
    fi
fi

if [ "$SKIP_BIGBED" != "true" ]; then
    # Create UCSC bin directory if it doesn't exist
    mkdir -p "$UCSC_BIN_DIR"
    
    # Detect OS and architecture
    OS=$(uname -s)
    ARCH=$(uname -m)
    
    echo -e "${YELLOW}Detected OS: $OS, Architecture: $ARCH${NC}"
    
    # Determine the correct UCSC binary path
    case "$OS" in
        Linux)
            if [ "$ARCH" = "x86_64" ]; then
                UCSC_PATH="linux.x86_64"
            else
                echo -e "${RED}Error: Unsupported Linux architecture: $ARCH${NC}"
                echo -e "${YELLOW}bigBedToBed is only available for x86_64 on Linux${NC}"
                SKIP_BIGBED=true
            fi
            ;;
        Darwin)
            if [ "$ARCH" = "x86_64" ]; then
                UCSC_PATH="macOSX.x86_64"
            elif [ "$ARCH" = "arm64" ]; then
                UCSC_PATH="macOSX.arm64"
            else
                echo -e "${RED}Error: Unsupported macOS architecture: $ARCH${NC}"
                SKIP_BIGBED=true
            fi
            ;;
        *)
            echo -e "${RED}Error: Unsupported operating system: $OS${NC}"
            echo -e "${YELLOW}bigBedToBed is only available for Linux and macOS${NC}"
            SKIP_BIGBED=true
            ;;
    esac
    
    if [ "$SKIP_BIGBED" != "true" ]; then
        BIGBED_URL="https://hgdownload.soe.ucsc.edu/admin/exe/$UCSC_PATH/bigBedToBed"
        
        echo -e "${GREEN}Downloading bigBedToBed from UCSC...${NC}"
        echo -e "${YELLOW}URL: $BIGBED_URL${NC}"
        
        # Check if wget or curl is available
        if command -v wget &> /dev/null; then
            wget -O "$UCSC_BIN_DIR/bigBedToBed" "$BIGBED_URL"
        elif command -v curl &> /dev/null; then
            curl -L -o "$UCSC_BIN_DIR/bigBedToBed" "$BIGBED_URL"
        else
            echo -e "${RED}Error: Neither wget nor curl is available.${NC}"
            echo -e "${YELLOW}Please install wget or curl and try again.${NC}"
            SKIP_BIGBED=true
        fi
        
        if [ $? -eq 0 ] && [ "$SKIP_BIGBED" != "true" ]; then
            chmod +x "$UCSC_BIN_DIR/bigBedToBed"
            echo -e "${GREEN}✓ bigBedToBed downloaded successfully!${NC}"
            echo -e "${YELLOW}bigBedToBed is located at: $UCSC_BIN_DIR/bigBedToBed${NC}"
        elif [ "$SKIP_BIGBED" != "true" ]; then
            echo -e "${RED}Error: Failed to download bigBedToBed.${NC}"
        fi
    fi
fi

# =============================================
# Summary
# =============================================
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Installation Summary${NC}"
echo -e "${BLUE}=========================================${NC}"

if [ "$SKIP_BIGBED" != "true" ] || [ -f "$UCSC_BIN_DIR/bigBedToBed" ]; then
    echo -e "${GREEN}✓ bigBedToBed:${NC} $UCSC_BIN_DIR/bigBedToBed"
fi

echo -e "\n${YELLOW}To use this tool, add it to your PATH:${NC}"
echo -e "${YELLOW}  export PATH=\"$UCSC_BIN_DIR:\$PATH\"${NC}"

chmod +x $UCSC_BIN_DIR/bigBedToBed

echo -e "\n${GREEN}Setup complete!${NC}"
