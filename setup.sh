#!/bin/bash
# Setup script for YouTrack KB Helper

echo "====================================="
echo "YouTrack KB Helper - Setup Script"
echo "====================================="
echo ""

# Check if venv exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists."
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing old virtual environment..."
        rm -rf venv
    else
        echo "✓ Using existing virtual environment"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        echo "Try: python -m venv venv"
        exit 1
    fi
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    read -p "Do you want to create one now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✓ Created .env file from template"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env file and add your credentials:"
        echo "   - YOUTRACK_BASE_URL"
        echo "   - YOUTRACK_TOKEN"
        echo ""
        echo "Run: nano .env  (or use your preferred editor)"
    fi
else
    echo "✓ .env file exists"
fi

echo ""
echo "====================================="
echo "✅ Setup complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Configure your credentials (if not done):"
echo "   nano .env"
echo ""
echo "3. Test the connection:"
echo "   python kb-helper.py test-connection"
echo ""
echo "4. Run analysis:"
echo "   python kb-helper.py stale-content YOUR_PROJECT_ID"
echo ""
echo "To deactivate the virtual environment later:"
echo "   deactivate"
echo ""
