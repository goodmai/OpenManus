#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "Stopping eth_simulateV1 test network..."

# Stop services
docker compose down

echo ""
echo "Network stopped."
echo "To also remove data volumes, run:"
echo "  docker compose down -v"
