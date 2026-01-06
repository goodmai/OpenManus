#!/bin/bash
set -e

echo "Building consensus client image..."
cd consensus-client
docker build -t consensus-client:local .
cd ..

echo "Starting local network with 2 consensus + 2 execution clients..."
docker compose down -v 2>/dev/null || true
docker compose up -d

echo "Waiting for services to be healthy..."
sleep 30

echo "Checking service status..."
docker compose ps

echo ""
echo "Service URLs:"
echo "  op-geth (ec-1): http://127.0.0.1:18545"
echo "  op-geth (ec-2): http://127.0.0.1:28545"
echo "  op-reth (ec-3): http://127.0.0.1:38545"
echo "  waves-node-1:   http://127.0.0.1:16869"
echo "  waves-node-2:   http://127.0.0.1:26869"

echo ""
echo "To view logs: docker compose logs -f [service_name]"
echo "To stop: docker compose down"
