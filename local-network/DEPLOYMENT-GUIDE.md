# ETH_SIMULATEV1 Integration - Quick Start Guide

## Deployment Summary

This guide provides step-by-step instructions to deploy and test the eth_simulateV1 integration in a local network with 2 consensus clients and 2 execution clients.

## Prerequisites

Before starting, ensure you have:
- Docker installed (v20.10+)
- Docker Compose installed (v2.0+)
- Python 3.8+ with pip
- At least 8GB RAM available
- At least 20GB disk space available

## Quick Deployment (5 Steps)

### Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install jq (for JSON processing in health checks)
# Ubuntu/Debian:
sudo apt-get install jq

# macOS:
brew install jq

# Or use package manager of your choice
```

### Step 2: Build Images

```bash
# Make scripts executable (if not already)
chmod +x *.sh

# Build all required images
./build-images.sh
```

This will:
- Build consensus-client from source
- Pull op-geth image
- Pull op-reth image with eth_simulateV1

**Expected Time**: 5-10 minutes (depending on network speed)

### Step 3: Start Network

```bash
# Deploy the complete network
./start-network.sh
```

This will:
- Stop any existing network
- Start all containers (ec-1, ec-2, ec-3, waves-node-1, waves-node-2)
- Wait for services to become healthy
- Display status and service URLs

**Expected Time**: 3-5 minutes

### Step 4: Verify Health

```bash
# Check network health
./health-check.sh
```

Expected output:
```
==========================================
Local Network Health Check
==========================================

1. Checking Docker Compose status...
All services should show as "healthy"

2. Checking execution clients...
   ✓ op-geth (ec-1) - Block: 0x123
   ✓ op-geth (ec-2) - Block: 0x123
   ✓ op-reth (ec-3) - Block: 0x123

3. Checking consensus clients...
   ✓ waves-node-1 - Height: 123
   ✓ waves-node-2 - Height: 123

4. Testing eth_simulateV1...
   ✓ eth_simulateV1 - Method available and responding
```

### Step 5: Run Tests

```bash
# Run comprehensive eth_simulateV1 tests
python3 test_eth_simulate_v1.py
```

Expected output:
```
================================================================================
ETH_SIMULATEV1 TESTING
================================================================================

1. Checking connections...
   op-geth: ✓ Connected
   op-reth: ✓ Connected

2. Checking block production...
   op-geth block: 42
   op-reth block: 42
   In sync: ✓ Yes

3. Testing eth_simulateV1 method existence...
   ✓ op-geth: eth_simulateV1 method exists
   ✓ op-reth: eth_simulateV1 method exists

...

✓✓✓ ALL TESTS PASSED ✓✓✓
```

## Service Endpoints

After successful deployment, the following services will be available:

### Execution Clients
- **op-geth (ec-1)**: http://127.0.0.1:18545
- **op-geth (ec-2)**: http://127.0.0.1:28545
- **op-reth (ec-3)**: http://127.0.0.1:38545 (eth_simulateV1 available here)

### Consensus Clients
- **waves-node-1**: http://127.0.0.1:16869
- **waves-node-2**: http://127.0.0.1:26869

### Engine API
- **ec-1 Engine**: http://127.0.0.1:18551
- **ec-2 Engine**: http://127.0.0.1:28551
- **ec-3 Engine**: http://127.0.0.1:38551

## Monitoring

### Continuous Monitoring

```bash
# Start continuous network monitoring
./monitor-network.sh
```

This will:
- Display block numbers for all execution clients
- Show sync status
- Log to monitoring.log
- Alert on issues

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f ec-3
docker compose logs -f waves-node-1

# Last 100 lines
docker compose logs --tail=100 ec-1
```

### Check Status

```bash
# Container status
docker compose ps

# Resource usage
docker stats

# Network connectivity
curl http://127.0.0.1:18545 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

## Testing eth_simulateV1

### Manual Test

```bash
# Test eth_simulateV1 method
curl -X POST http://127.0.0.1:38545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "eth_simulateV1",
    "params": [{
      "pendingTransactions": []
    }],
    "id": 1
  }'
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "simulatedBlocks": [...],
    "pendingTransactions": []
  }
}
```

### With Transaction

```bash
# Get latest block
BLOCK=$(curl -s http://127.0.0.1:38545 -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  | jq -r '.result')

# Test with transaction (replace with actual signed tx)
curl -X POST http://127.0.0.1:38545 \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"eth_simulateV1\",
    \"params\": [{
      \"pendingTransactions\": [\"0x...\"],
      \"blockNumber\": $((16#$BLOCK + 1))
    }],
    \"id\": 1
  }"
```

## Troubleshooting

### Common Issues

#### Issue: Containers Not Starting

**Symptoms**: Containers exit immediately or show errors

**Solutions**:
```bash
# Check logs
docker compose logs [service_name]

# Check port conflicts
netstat -tuln | grep -E "18545|28545|38545|16869|26869"

# Restart network
docker compose down -v
./start-network.sh
```

#### Issue: Services Not Healthy

**Symptoms**: Health checks fail, containers restart repeatedly

**Solutions**:
```bash
# Check resource availability
docker stats

# Increase wait time
sleep 120  # Wait 2 minutes

# Check logs for errors
docker compose logs ec-1
docker compose logs ec-3
```

#### Issue: eth_simulateV1 Not Available

**Symptoms**: Method not found error when calling eth_simulateV1

**Solutions**:
```bash
# Check if op-reth image has eth_simulateV1
docker exec ec-3 reth --help | grep simulate

# Verify op-reth is running
docker compose logs ec-3 | grep "simulate"

# Check op-reth configuration
docker exec ec-3 cat /etc/config.toml
```

#### Issue: Block Sync Problems

**Symptoms**: Different block numbers across execution clients

**Solutions**:
```bash
# Check peer connections
docker exec ec-1 geth --exec "admin.peers" attach http://localhost:8545

# Check network ID consistency
curl http://127.0.0.1:18545 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"net_version","params":[],"id":1}'
curl http://127.0.0.1:38545 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"net_version","params":[],"id":1}'
```

### Recovery Procedures

#### Full Reset

```bash
# Stop everything
docker compose down -v

# Clean up images (optional)
docker system prune -a

# Restart from scratch
./build-images.sh
./start-network.sh
```

#### Partial Restart

```bash
# Restart specific service
docker compose restart ec-3

# Check status
./health-check.sh
```

## Stopping the Network

```bash
# Stop all services (keeps data)
docker compose down

# Stop and remove all data
docker compose down -v
```

## Performance Optimization

### For Development

The default configuration is optimized for:
- Fast startup (3-5 minutes)
- Adequate resources (8GB RAM)
- Full synchronization

### For Testing

Consider:
- Increasing block production speed
- Reducing sync time
- Increasing log verbosity

### For CI/CD

Automate with:
```bash
# Non-interactive deployment
export COMPOSE_DOCKER_CLI_BUILD=0
export DOCKER_BUILDKIT=0
./build-images.sh
docker compose up -d
sleep 300  # Wait for sync
python3 test_eth_simulate_v1.py
```

## Next Steps

After successful deployment:

1. **Run Full Test Suite**
   ```bash
   python3 test_eth_simulate_v1.py
   ```

2. **Monitor Network**
   ```bash
   ./monitor-network.sh &
   ```

3. **Start Developing**
   - Connect Metamask to http://127.0.0.1:18545
   - Use Remix to deploy contracts
   - Test eth_simulateV1 in your applications

4. **Review Documentation**
   - Read README.md for detailed info
   - Check TEST-REPORT.md for test results
   - Review INTEGRATION-SUMMARY.md for architecture

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs: `docker compose logs [service]`
3. Check network health: `./health-check.sh`
4. Verify configuration files
5. Review eth_simulateV1 specification

## File Locations

Key files for reference:
- `docker-compose.yml` - Main orchestration
- `docker/services/op-reth.yml` - op-reth configuration
- `configs/ec-common/genesis.json` - Genesis block
- `test_eth_simulate_v1.py` - Test suite
- `health-check.sh` - Health verification
- `monitor-network.sh` - Continuous monitoring

## Success Checklist

- [ ] All containers started successfully
- [ ] All services show as healthy
- [ ] Block production is active
- [ ] Network is synchronized
- [ ] eth_simulateV1 is available on op-reth
- [ ] Basic tests pass
- [ ] Transaction simulation works
- [ ] Both consensus clients are active
- [ ] All execution clients are in sync

---

**Ready to Deploy? Run:**
```bash
pip install -r requirements.txt && ./build-images.sh && ./start-network.sh && ./health-check.sh && python3 test_eth_simulate_v1.py
```

This will deploy, verify, and test the entire network in one go!

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-06  
**Tested With**: Docker v20.10, Docker Compose v2.0, Python 3.8+
