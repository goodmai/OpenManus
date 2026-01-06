#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "Starting eth_simulateV1 test network..."

# Generate genesis if not already done
if [ ! -f "configs/consensus/genesis.ssz" ]; then
    echo "Generating genesis configuration..."
    ./scripts/generate-genesis.sh
fi

# Create data directories
mkdir -p data/ec-opgeth data/ec-opreth data/cc-lighthouse data/cc-prysm data/validator-lighthouse

# Pull images
echo "Pulling Docker images..."
docker compose pull

# Start services
echo "Starting services..."
docker compose up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 10

# Check service status
echo "Service status:"
docker compose ps

echo ""
echo "Network started successfully!"
echo ""
echo "Available endpoints:"
echo "  op-geth RPC: http://127.0.0.1:18545"
echo "  op-reth RPC: http://127.0.0.1:28545"
echo "  Lighthouse API: http://127.0.0.1:15052"
echo "  Prysm API: http://127.0.0.1:14000"
echo ""
echo "View logs: docker compose logs -f"
echo "Stop network: docker compose down"
echo "Stop and clean: docker compose down -v"
