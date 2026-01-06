#!/bin/bash

set -e

CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/configs"
mkdir -p "$CONFIG_DIR/logs/ec-1"

echo "Generating test network configuration..."

# Generate JWT secret
if [ ! -f "$CONFIG_DIR/jwtsecret.hex" ]; then
    openssl rand -hex 32 > "$CONFIG_DIR/jwtsecret.hex"
    echo "Generated JWT secret: $CONFIG_DIR/jwtsecret.hex"
fi

# Generate P2P key for ec-1
if [ ! -f "$CONFIG_DIR/p2p-key-1.hex" ]; then
    head -c 32 /dev/urandom | xxd -p -c 32 > "$CONFIG_DIR/p2p-key-1.hex"
    echo "Generated P2P key for ec-1: $CONFIG_DIR/p2p-key-1.hex"
fi

# Generate P2P key for ec-2
if [ ! -f "$CONFIG_DIR/p2p-key-2.hex" ]; then
    head -c 32 /dev/urandom | xxd -p -c 32 > "$CONFIG_DIR/p2p-key-2.hex"
    echo "Generated P2P key for ec-2: $CONFIG_DIR/p2p-key-2.hex"
fi

echo ""
echo "Configuration files generated successfully!"
echo "Config directory: $CONFIG_DIR"
