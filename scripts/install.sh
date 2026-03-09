#!/bin/bash
# ProBharatAI One-Command Installer for Mac/Linux
set -e

echo "🤖 ProBharatAI - AI Desktop Automation Platform"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Python not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python3
    else
        sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
    fi
    PYTHON=python3
fi

echo -e "${GREEN}✅ Python found: $($PYTHON --version)${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install node
    else
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
fi

echo -e "${GREEN}✅ Node.js found: $(node --version)${NC}"

# Clone or update
INSTALL_DIR="$HOME/.probharatai"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${BLUE}📦 Updating ProBharatAI...${NC}"
    cd "$INSTALL_DIR"
    git pull
else
    echo -e "${BLUE}📦 Downloading ProBharatAI...${NC}"
    git clone https://github.com/probharatai/probharatai.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Create virtual environment
echo -e "${BLUE}🐍 Setting up Python environment...${NC}"
$PYTHON -m venv venv
source venv/bin/activate

# Install backend
pip install -r backend/requirements.txt
python -m playwright install chromium

# Install frontend
echo -e "${BLUE}⚛️  Installing frontend...${NC}"
cd frontend && npm install && cd ..

# Setup env
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
fi

# Create CLI alias
echo "alias probharatai='cd $INSTALL_DIR && source venv/bin/activate && python cli.py'" >> ~/.bashrc
echo "alias probharatai='cd $INSTALL_DIR && source venv/bin/activate && python cli.py'" >> ~/.zshrc 2>/dev/null

echo ""
echo -e "${GREEN}✅ ProBharatAI installed successfully!${NC}"
echo ""
echo "🚀 Quick Start:"
echo "   probharatai start     # Start the platform"
echo "   probharatai status    # Check status"
echo "   probharatai run 'Search AI jobs on LinkedIn'"
echo ""
echo "📖 Dashboard: http://localhost:3000"
echo "🔧 API:       http://localhost:8000"
echo ""
