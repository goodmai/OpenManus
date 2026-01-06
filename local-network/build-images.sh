#!/bin/bash
set -e

echo "Building all required Docker images..."

# Build consensus client
echo "Building consensus-client image..."
cd consensus-client
docker build -t consensus-client:local .
cd ..

# Pull op-geth image
echo "Pulling op-geth image..."
docker pull ghcr.io/unitsnetwork/op-geth:v1.101603.0-1

# Pull op-reth image (with eth_simulateV1)
echo "Pulling op-reth image with eth_simulateV1..."
docker pull ghcr.io/unitsnetwork/op-reth:simulate-v1-latest || echo "Note: op-reth image may not exist yet"

echo "All images built successfully!"
