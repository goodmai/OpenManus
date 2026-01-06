#!/bin/bash
# Monitoring script for local network
# Continuously monitors block production and sync status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/monitoring.log"
INTERVAL=${1:-5}  # Default to 5 second intervals

echo "Starting network monitoring (interval: ${INTERVAL}s)"
echo "Log file: $LOG_FILE"
echo "Press Ctrl+C to stop"
echo ""

# Function to get block numbers
get_block_numbers() {
  local ec1=$(curl -s http://127.0.0.1:18545 -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' 2>/dev/null | jq -r '.result' 2>/dev/null | sed 's/^0x//' | xargs -I {} printf "%d" {} 2>/dev/null || echo "0")
  
  local ec2=$(curl -s http://127.0.0.1:28545 -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' 2>/dev/null | jq -r '.result' 2>/dev/null | sed 's/^0x//' | xargs -I {} printf "%d" {} 2>/dev/null || echo "0")
  
  local ec3=$(curl -s http://127.0.0.1:38545 -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' 2>/dev/null | jq -r '.result' 2>/dev/null | sed 's/^0x//' | xargs -I {} printf "%d" {} 2>/dev/null || echo "0")
  
  echo "$ec1 $ec2 $ec3"
}

# Function to check service health
check_services() {
  local all_ok=true
  
  # Check ec-1
  if ! curl -s http://127.0.0.1:18545 -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' > /dev/null 2>&1; then
    echo "WARNING: ec-1 not responding" >> "$LOG_FILE"
    all_ok=false
  fi
  
  # Check ec-2
  if ! curl -s http://127.0.0.1:28545 -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' > /dev/null 2>&1; then
    echo "WARNING: ec-2 not responding" >> "$LOG_FILE"
    all_ok=false
  fi
  
  # Check ec-3
  if ! curl -s http://127.0.0.1:38545 -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' > /dev/null 2>&1; then
    echo "WARNING: ec-3 not responding" >> "$LOG_FILE"
    all_ok=false
  fi
  
  # Check waves-node-1
  if ! curl -s http://127.0.0.1:16869/debug/blocks > /dev/null 2>&1; then
    echo "WARNING: waves-node-1 not responding" >> "$LOG_FILE"
    all_ok=false
  fi
  
  # Check waves-node-2
  if ! curl -s http://127.0.0.1:26869/debug/blocks > /dev/null 2>&1; then
    echo "WARNING: waves-node-2 not responding" >> "$LOG_FILE"
    all_ok=false
  fi
  
  echo "$all_ok"
}

# Initialize log
echo "$(date): Starting monitoring" > "$LOG_FILE"

# Get initial block numbers
read -r BLOCK1 BLOCK2 BLOCK3 <<< $(get_block_numbers)
echo "Initial blocks - ec-1: $BLOCK1, ec-2: $BLOCK2, ec-3: $BLOCK3"

# Monitor loop
while true; do
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
  
  # Get current block numbers
  read -r NEW_BLOCK1 NEW_BLOCK2 NEW_BLOCK3 <<< $(get_block_numbers)
  
  # Check if blocks are advancing
  EC1_ADVANCED=$((NEW_BLOCK1 - BLOCK1))
  EC2_ADVANCED=$((NEW_BLOCK2 - BLOCK2))
  EC3_ADVANCED=$((NEW_BLOCK3 - BLOCK3))
  
  # Check sync status
  MAX_BLOCK=$((EC1_ADVANCED > EC2_ADVANCED ? EC1_ADVANCED : EC2_ADVANCED))
  MAX_BLOCK=$((MAX_BLOCK > EC3_ADVANCED ? MAX_BLOCK : EC3_ADVANCED))
  MIN_BLOCK=$((EC1_ADVANCED < EC2_ADVANCED ? EC1_ADVANCED : EC2_ADVANCED))
  MIN_BLOCK=$((MIN_BLOCK < EC3_ADVANCED ? MIN_BLOCK : EC3_ADVANCED))
  
  SYNC_DIFF=$((MAX_BLOCK - MIN_BLOCK))
  
  # Log to file
  {
    echo "$TIMESTAMP - ec-1: $NEW_BLOCK1 (+$EC1_ADVANCED), ec-2: $NEW_BLOCK2 (+$EC2_ADVANCED), ec-3: $NEW_BLOCK3 (+$EC3_ADVANCED)"
    echo "$TIMESTAMP - Sync diff: $SYNC_DIFF blocks"
    
    # Check sync status
    if [ "$SYNC_DIFF" -gt "3" ]; then
      echo "$TIMESTAMP - WARNING: Clients are out of sync (diff: $SYNC_DIFF blocks)"
    fi
    
    # Check services
    ALL_SERVICES_OK=$(check_services)
    if [ "$ALL_SERVICES_OK" != "true" ]; then
      echo "$TIMESTAMP - WARNING: Some services are not responding"
    fi
  } >> "$LOG_FILE"
  
  # Display to console
  printf "\r%s - ec-1: %5d (+%2d) | ec-2: %5d (+%2d) | ec-3: %5d (+%2d) | Sync diff: %d" \
    "$TIMESTAMP" "$NEW_BLOCK1" "$EC1_ADVANCED" "$NEW_BLOCK2" "$EC2_ADVANCED" "$NEW_BLOCK3" "$EC3_ADVANCED" "$SYNC_DIFF"
  
  # Alert if out of sync
  if [ "$SYNC_DIFF" -gt "3" ]; then
    echo ""
    echo "WARNING: Clients out of sync! Check $LOG_FILE for details"
  fi
  
  # Update previous values
  BLOCK1=$NEW_BLOCK1
  BLOCK2=$NEW_BLOCK2
  BLOCK3=$NEW_BLOCK3
  
  sleep "$INTERVAL"
done
