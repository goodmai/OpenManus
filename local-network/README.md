# Ethereum Local Network with 2 Consensus + 2 Execution Clients

This setup provides a local Ethereum development network with:
- **2 Consensus Clients**: waves-node-1, waves-node-2
- **2 Execution Clients**: op-geth (ec-1, ec-2), op-reth with eth_simulateV1 (ec-3)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Local Network Setup                       │
├─────────────────────┬───────────────────┬───────────────────┤
│  Consensus Client   │  Execution Client │    Purpose        │
├─────────────────────┼───────────────────┼───────────────────┤
│  waves-node-1        │  op-geth (ec-1)   │ Standard OP Stack │
│  waves-node-2        │  op-geth (ec-2)   │ Load balancing    │
│                     │  op-reth (ec-3)   │ eth_simulateV1    │
└─────────────────────┴───────────────────┴───────────────────┘
```

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- At least 8GB RAM
- At least 20GB free disk space

## Quick Start

### 1. Build Images

```bash
chmod +x build-images.sh
./build-images.sh
```

### 2. Start Network

```bash
chmod +x start-network.sh
./start-network.sh
```

### 3. Run Tests

```bash
chmod +x test_eth_simulate_v1.py
python3 test_eth_simulate_v1.py
```

## Service Details

### Execution Clients

| Service | Port | RPC URL | Engine API | Purpose |
|---------|------|---------|------------|---------|
| op-geth (ec-1) | 18545 | http://127.0.0.1:18545 | http://127.0.0.1:18551 | Primary execution |
| op-geth (ec-2) | 28545 | http://127.0.0.1:28545 | http://127.0.0.1:28551 | Secondary execution |
| op-reth (ec-3) | 38545 | http://127.0.0.1:38545 | http://127.0.0.1:38551 | eth_simulateV1 testing |

### Consensus Clients

| Service | Port | API URL | Purpose |
|---------|------|---------|---------|
| waves-node-1 | 16869 | http://127.0.0.1:16869 | Primary consensus |
| waves-node-2 | 26869 | http://127.0.0.1:26869 | Secondary consensus |

## Testing eth_simulateV1

The `test_eth_simulate_v1.py` script performs the following tests:

1. **Connection Check**: Verify both execution clients are accessible
2. **Block Production**: Ensure both clients are producing blocks in sync
3. **Method Existence**: Confirm eth_simulateV1 is available on op-reth
4. **Basic Simulation**: Test empty transaction simulation
5. **Transaction Simulation**: Test with actual transactions
6. **Depository Simulation**: Test depository-related scenarios
7. **Result Comparison**: Verify op-geth and op-reth return identical results

### Running Tests

```bash
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

4. Testing basic simulation...
   ✓ op-geth: Basic simulation successful
   ✓ op-reth: Basic simulation successful
   ✓ Results from op-geth and op-reth are IDENTICAL

...

✓✓✓ ALL TESTS PASSED ✓✓✓
```

## Manual Testing

### Connect to Metamask

1. Open Metamask
2. Add network:
   - Network name: Waves Unit0 dev
   - RPC URL: http://127.0.0.1:18545
   - Chain ID: 1337
   - Currency symbol: Unit0

### Deploy Contract using Remix

1. Open https://remix.ethereum.org
2. Compile HelloWorld contract
3. Deploy with:
   - Environment: "Injected Provider - Metamask"
   - Account: Choose from available accounts

### Manual eth_simulateV1 Calls

```bash
# Basic call
curl -X POST http://127.0.0.1:38545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "eth_simulateV1",
    "params": [{"pendingTransactions": []}],
    "id": 1
  }'

# With transaction
curl -X POST http://127.0.0.1:38545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "eth_simulateV1",
    "params": [{
      "pendingTransactions": ["0x..."],
      "blockNumber": 100
    }],
    "id": 1
  }'
```

## Monitoring

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f ec-1
docker compose logs -f ec-3
docker compose logs -f waves-node-1
```

### Check Status

```bash
docker compose ps
```

### Check Health

```bash
# Check if services are responding
curl http://127.0.0.1:18545 -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
curl http://127.0.0.1:38545 -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

## Troubleshooting

### Services Not Starting

1. Check logs:
   ```bash
   docker compose logs [service_name]
   ```

2. Ensure ports are not in use:
   ```bash
   netstat -tuln | grep -E "18545|28545|38545|16869|26869"
   ```

3. Check disk space:
   ```bash
   df -h
   ```

4. Restart network:
   ```bash
   docker compose down -v
   ./start-network.sh
   ```

### eth_simulateV1 Not Available

1. Verify op-reth image has eth_simulateV1:
   ```bash
   docker exec ec-3 reth --help | grep simulate
   ```

2. Check op-reth logs:
   ```bash
   docker compose logs ec-3
   ```

### Block Sync Issues

1. Check peer connections:
   ```bash
   docker exec ec-1 geth --exec "admin.peers" attach http://localhost:8545
   docker exec ec-3 geth --exec "admin.peers" attach http://localhost:8545
   ```

2. Check network ID:
   ```bash
   curl http://127.0.0.1:18545 -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"net_version","params":[],"id":1}'
   ```

## Configuration Files

### Docker Compose

- `docker-compose.yml`: Main orchestration file
- `docker/services/op-geth.yml`: op-geth service definition
- `docker/services/op-reth.yml`: op-reth service definition

### Network Config

- `configs/ec-common/genesis.json`: Genesis block configuration
- `configs/ec-common/config.toml`: Client configuration
- `configs/ec-common/jwtsecret.hex`: JWT secret for Engine API

### Keys

- `configs/ec-common/p2p-key-*.hex`: Node keys for discovery
- `configs/ec-common/jwtsecret.hex`: JWT token for Engine API authentication

## Stopping the Network

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: Deletes all data)
docker compose down -v
```

## Development

### Rebuild Consensus Client

```bash
cd consensus-client
docker build -t consensus-client:local .
cd ..
```

### Modify Configuration

1. Edit files in `configs/`
2. Restart network:
   ```bash
   docker compose down -v
   ./start-network.sh
   ```

## Performance Considerations

- Each execution client uses ~2GB RAM
- Each consensus client uses ~1GB RAM
- Total memory usage: ~6-8GB
- Each client stores ~1-2GB of blockchain data

## Security Notes

- This is for development/testing only
- Do not use in production
- Private keys are exposed in configuration
- JWT secrets are not secure

## References

- [Ethereum JSON-RPC API](https://ethereum.org/en/developers/docs/apis/json-rpc/)
- [Optimism (OP) Stack](https://community.optimism.io/docs/developers/)
- [op-reth](https://github.com/paradigmxyz/reth)
- [waves-node](https://github.com/wavesplatform/Waves)

## Support

For issues and questions:
1. Check logs: `docker compose logs [service_name]`
2. Review this README
3. Check eth_simulateV1 specification
4. Contact development team
