#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "====================================================================="
echo "eth_simulateV1 Local Network - Quick Setup"
echo "====================================================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker is installed: $(docker --version)"
echo "✓ Docker Compose is installed: $(docker compose version)"
echo ""

# Check if Python is available for tests
if command -v python3 &> /dev/null; then
    echo "✓ Python 3 is available: $(python3 --version)"
else
    echo "⚠ Python 3 not found. Tests will not be available."
fi

echo ""

# Install Python dependencies if available
if command -v pip3 &> /dev/null; then
    echo "Installing Python dependencies..."
    pip3 install httpx --quiet || echo "⚠ Failed to install httpx. Tests may not work."
fi

echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x "$SCRIPT_DIR/start.sh"
chmod +x "$SCRIPT_DIR/stop.sh"
chmod +x "$SCRIPT_DIR/generate-genesis.sh"
chmod +x "$SCRIPT_DIR/health_check.py"
echo "✓ Scripts are executable"
echo ""

# Generate genesis configuration
echo "Generating genesis configuration..."
cd "$PROJECT_ROOT"
"$SCRIPT_DIR/generate-genesis.sh"
echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p data/ec-opgeth data/ec-opreth data/cc-lighthouse data/cc-prysm data/validator-lighthouse
mkdir -p logs/ec-opgeth logs/ec-opreth logs/cc-lighthouse logs/cc-prysm logs/validator-lighthouse
echo "✓ Data directories created"
echo ""

# Pull Docker images
echo "Pulling Docker images (this may take a few minutes)..."
docker compose pull
echo ""

echo "====================================================================="
echo "Setup Complete!"
echo "====================================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the network:"
echo "   ./scripts/start.sh"
echo ""
echo "2. Wait for services to initialize (~2 minutes)"
echo ""
echo "3. Check network health:"
echo "   python3 scripts/health_check.py"
echo ""
echo "4. Run tests:"
echo "   python3 tests/test_eth_simulateV1.py"
echo ""
echo "For more information, see README.md"
echo ""
