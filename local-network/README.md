# eth_simulateV1 Local Network Setup

This directory contains a complete Docker Compose setup for testing `eth_simulateV1` in a local Ethereum network with 2 consensus clients and 2 execution clients.

## Architecture

### Components

1. **Execution Clients (2)**
   - **op-geth** (standard): `ghcr.io/unitsnetwork/op-geth:v1.101603.0-1`
     - Port: 18545 (HTTP RPC), 18546 (WebSocket), 18551 (Engine API)
   - **op-reth** (modified with eth_simulateV1): `ghcr.io/unitsnetwork/op-reth:simulate-v1-1.0.0`
     - Port: 28545 (HTTP RPC), 28546 (WebSocket), 28551 (Engine API)

2. **Consensus Clients (2)**
   - **Lighthouse**: `sigp/lighthouse:v5.2.1`
     - Connected to: ec-opgeth
     - Port: 15052 (HTTP API), 9000 (P2P)
   - **Prysm**: `gcr.io/prysmaticlabs/prysm/beacon-chain:v5.1.0`
     - Connected to: ec-opreth
     - Port: 14000 (HTTP API), 13500 (GRPC Gateway), 13000 (P2P)

3. **Validator**
   - **Lighthouse Validator**: `sigp/lighthouse:v5.2.1`
     - Connected to: cc-lighthouse
     - Participates in block production

4. **Test Runner**
   - **Python**: `python:3.12-slim`
     - Contains test scripts
     - Can run tests and diagnostics

### Network Topology

```
┌─────────────┐         ┌─────────────┐
│  Lighthouse │◄────────┤  op-geth    │
│  (CC-1)     │         │  (EC-1)     │
└─────────────┘         └─────────────┘
       │                       │
       │                       │
       │            ┌──────────┘
       │            │
       │       ┌────▼──────────────┐
       └───────┤ eth_testnet       │
               │   Network        │
       ┌───────┴────▲──────────────┘
       │            │
       │            │
       ▼            │
┌─────────────┐     │
│   Prysm     │──────────►┌─────────────┐
│  (CC-2)     │          │  op-reth    │
└─────────────┘          │  (EC-2)     │
                         │ (simulateV1)│
                         └─────────────┘
```

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- Python 3.12 (for running test scripts)
- At least 8GB RAM available

## Quick Start

### 1. Clone and Setup

```bash
cd /home/engine/project/local-network
```

### 2. Generate Genesis Configuration

```bash
./scripts/generate-genesis.sh
```

This script generates:
- Consensus genesis state (`genesis.ssz`)
- Validator keys
- Deposit data
- Configuration files for both Lighthouse and Prysm

### 3. Start the Network

```bash
./scripts/start.sh
```

This will:
- Pull all required Docker images
- Create data directories
- Start all containers
- Display status and endpoint information

### 4. Wait for Services to Initialize

The network typically takes 1-2 minutes to fully initialize. You can monitor progress with:

```bash
docker compose logs -f
```

### 5. Run Health Check

```bash
python3 scripts/health_check.py
```

This will check:
- Container status
- RPC endpoint availability
- eth_simulateV1 support
- Block production
- Log errors

### 6. Run Tests

```bash
# Activate test runner container
docker compose --profile tests up -d test-runner

# Run tests
docker compose exec test-runner python3 /tests/test_eth_simulateV1.py

# Or run tests directly from host
python3 tests/test_eth_simulateV1.py
```

## API Endpoints

### Execution Clients

**op-geth (standard)**
- RPC: `http://127.0.0.1:18545`
- WebSocket: `ws://127.0.0.1:18546`
- Engine API: `http://127.0.0.1:18551`

**op-reth (with eth_simulateV1)**
- RPC: `http://127.0.0.1:28545`
- WebSocket: `ws://127.0.0.1:28546`
- Engine API: `http://127.0.0.1:28551`

### Consensus Clients

**Lighthouse**
- HTTP API: `http://127.0.0.1:15052`
- P2P: `127.0.0.1:9000`

**Prysm**
- HTTP API: `http://127.0.0.1:14000`
- GRPC Gateway: `http://127.0.0.1:13500`
- P2P: `127.0.0.1:13000`

## Testing eth_simulateV1

### Example 1: Basic Simulation

```bash
curl -X POST http://127.0.0.1:28545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "eth_simulateV1",
    "params": [{
      "blockNumber": "latest",
      "transactions": []
    }],
    "id": 1
  }'
```

### Example 2: Simulate Transfer Transaction

```bash
curl -X POST http://127.0.0.1:28545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "eth_simulateV1",
    "params": [{
      "blockNumber": "latest",
      "transactions": [{
        "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
        "to": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
        "value": "0xde0b6b3a7640000",
        "gas": "0x5208",
        "gasPrice": "0x0"
      }]
    }],
    "id": 1
  }'
```

### Example 3: Compare op-geth vs op-reth

Use the Python test script to compare results:

```bash
python3 tests/test_eth_simulateV1.py
```

This will:
- Test basic simulation on both clients
- Simulate various transaction types
- Compare gas usage and results
- Test edge cases and error handling

## Configuration

### Genesis Configuration

The genesis configuration is located in:
- `configs/ec-common/genesis.json` - Execution layer genesis
- `configs/consensus/config-lighthouse.yaml` - Lighthouse config
- `configs/consensus/config-prysm.yml` - Prysm config

Key parameters:
- **Chain ID**: 1337
- **Slot Time**: 12 seconds
- **Epoch Duration**: 32 slots (6.4 minutes)
- **Validator Count**: 4 (configurable)

### Pre-funded Accounts

The genesis includes two pre-funded accounts:

1. **Account 1**
   - Address: `0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73`
   - Balance: 10,000 ETH
   - Private Key: `0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63`

2. **Account 2**
   - Address: `0xf17f52151EbEF6C7334FAD080c5704D77216b732`
   - Balance: 10,000 ETH + 1 wei
   - Private Key: `0xae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f`

## Scripts

### `scripts/start.sh`
Starts the entire network with all services.

### `scripts/stop.sh`
Stops all services without removing data.

### `scripts/health_check.py`
Comprehensive health check for all services.

### `scripts/generate-genesis.sh`
Generates genesis configuration and validator keys.

## Data Persistence

Data is stored in the `data/` directory:
- `data/ec-opgeth` - op-geth chain data
- `data/ec-opreth` - op-reth chain data
- `data/cc-lighthouse` - Lighthouse beacon data
- `data/cc-prysm` - Prysm beacon data
- `data/validator-lighthouse` - Validator data

To remove all data:
```bash
docker compose down -v
rm -rf data/*
```

## Troubleshooting

### Containers Won't Start

1. Check if ports are already in use:
   ```bash
   netstat -tuln | grep -E '18545|28545|15052|14000'
   ```

2. Check logs:
   ```bash
   docker compose logs ec-opgeth
   docker compose logs ec-opreth
   ```

### eth_simulateV1 Not Available

1. Verify op-reth container is running:
   ```bash
   docker ps | grep op-reth
   ```

2. Check op-reth logs for errors:
   ```bash
   docker compose logs ec-opreth | tail -100
   ```

3. Verify the image includes eth_simulateV1 support:
   ```bash
   docker exec ec-opreth reth --help | grep simulate
   ```

### No Blocks Being Produced

1. Check if validator is running:
   ```bash
   docker compose logs validator-lighthouse
   ```

2. Verify consensus clients are healthy:
   ```bash
   python3 scripts/health_check.py
   ```

3. Check synchronization status:
   ```bash
   curl http://127.0.0.1:15052/eth/v1/node/syncing
   curl http://127.0.0.1:14000/eth/v1/node/syncing
   ```

### Memory Issues

If you encounter memory issues:

1. Reduce the number of validators in genesis generation
2. Increase Docker memory limit
3. Stop unused containers:
   ```bash
   docker compose stop validator-lighthouse
   ```

## Maintenance

### Updating Images

```bash
docker compose pull
docker compose up -d
```

### Viewing Logs

All logs are stored in `logs/` directory:
- `logs/ec-opgeth/` - op-geth logs
- `logs/ec-opreth/` - op-reth logs
- `logs/cc-lighthouse/` - Lighthouse logs
- `logs/cc-prysm/` - Prysm logs

View logs in real-time:
```bash
docker compose logs -f
```

View specific container logs:
```bash
docker compose logs -f ec-opreth
```

### Restarting Services

Restart a specific service:
```bash
docker compose restart ec-opreth
```

Restart all services:
```bash
docker compose restart
```

## Advanced Usage

### Customizing Genesis

Edit `configs/ec-common/genesis.json` to modify:
- Pre-funded accounts
- Block parameters
- Fork configuration
- Gas settings

Then regenerate and restart:
```bash
./scripts/stop.sh
rm -rf data/*
./scripts/generate-genesis.sh
./scripts/start.sh
```

### Adding More Validators

Modify `scripts/generate-genesis.sh` to generate more validator keys, then restart.

### Testing with Custom Transactions

Create a custom test script in `tests/` and run it with:
```bash
python3 tests/your_test.py
```

## Documentation

- **Main README**: `../README.md`
- **Test Documentation**: `tests/README.md`
- **Test Reports**: `docs/test_report.md`

## Support

For issues or questions:
1. Check logs for error messages
2. Run health check: `python3 scripts/health_check.py`
3. Review troubleshooting section above

## License

This setup is provided as-is for testing and development purposes.
