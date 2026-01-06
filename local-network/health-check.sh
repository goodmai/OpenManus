#!/bin/bash
# Health check script for the local network
set -e

echo "=========================================="
echo "Local Network Health Check"
echo "=========================================="
echo ""

# Check Docker Compose status
echo "1. Checking Docker Compose status..."
docker compose ps

echo ""
echo "2. Checking execution clients..."

# Check op-geth (ec-1)
echo "   Checking op-geth (ec-1)..."
if curl -s http://127.0.0.1:18545 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' > /dev/null 2>&1; then
  BLOCK=$(curl -s http://127.0.0.1:18545 -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' | jq -r '.result' 2>/dev/null || echo "unknown")
  echo "   ✓ op-geth (ec-1) - Block: $BLOCK"
else
  echo "   ✗ op-geth (ec-1) - Not responding"
fi

# Check op-geth (ec-2)
echo "   Checking op-geth (ec-2)..."
if curl -s http://127.0.0.1:28545 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' > /dev/null 2>&1; then
  BLOCK=$(curl -s http://127.0.0.1:28545 -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' | jq -r '.result' 2>/dev/null || echo "unknown")
  echo "   ✓ op-geth (ec-2) - Block: $BLOCK"
else
  echo "   ✗ op-geth (ec-2) - Not responding"
fi

# Check op-reth (ec-3)
echo "   Checking op-reth (ec-3)..."
if curl -s http://127.0.0.1:38545 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' > /dev/null 2>&1; then
  BLOCK=$(curl -s http://127.0.0.1:38545 -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' | jq -r '.result' 2>/dev/null || echo "unknown")
  echo "   ✓ op-reth (ec-3) - Block: $BLOCK"
else
  echo "   ✗ op-reth (ec-3) - Not responding"
fi

echo ""
echo "3. Checking consensus clients..."

# Check waves-node-1
echo "   Checking waves-node-1..."
if curl -s http://127.0.0.1:16869/debug/blocks > /dev/null 2>&1; then
  HEIGHT=$(curl -s http://127.0.0.1:16869/debug/blocks | jq '.[0]' 2>/dev/null || echo "unknown")
  echo "   ✓ waves-node-1 - Height: $HEIGHT"
else
  echo "   ✗ waves-node-1 - Not responding"
fi

# Check waves-node-2
echo "   Checking waves-node-2..."
if curl -s http://127.0.0.1:26869/debug/blocks > /dev/null 2>&1; then
  HEIGHT=$(curl -s http://127.0.0.1:26869/debug/blocks | jq '.[0]' 2>/dev/null || echo "unknown")
  echo "   ✓ waves-node-2 - Height: $HEIGHT"
else
  echo "   ✗ waves-node-2 - Not responding"
fi

echo ""
echo "4. Testing eth_simulateV1..."

# Test eth_simulateV1 on op-reth
echo "   Testing eth_simulateV1 on op-reth (ec-3)..."
RESPONSE=$(curl -s http://127.0.0.1:38545 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_simulateV1","params":[{"pendingTransactions":[]}],"id":1}' 2>/dev/null || echo '{"error":"no response"}')

if echo "$RESPONSE" | grep -q "error"; then
  echo "   ✗ eth_simulateV1 - Method not available or error occurred"
  echo "   Response: $RESPONSE"
else
  echo "   ✓ eth_simulateV1 - Method available and responding"
fi

echo ""
echo "=========================================="
echo "Health check complete"
echo "=========================================="
