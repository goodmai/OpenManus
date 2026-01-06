# eth_simulateV1 Integration and Testing

This document describes the integration and testing setup for `eth_simulateV1` RPC method in a local Ethereum network environment.

## Overview

This project provides a complete Docker Compose environment for testing the `eth_simulateV1` RPC method with:
- 2 Consensus Clients (Lighthouse + Prysm)
- 2 Execution Clients (op-geth standard + op-reth modified)
- Validator setup for block production
- Comprehensive test suite
- Full documentation

## Project Structure

```
project/
├── local-network/          # Main Docker Compose setup
│   ├── docker-compose.yml
│   ├── README.md          # Detailed setup instructions
│   ├── scripts/
│   │   ├── setup.sh      # Quick setup script
│   │   ├── start.sh      # Start network
│   │   ├── stop.sh       # Stop network
│   │   ├── generate-genesis.sh
│   │   └── health_check.py
│   ├── tests/
│   │   ├── README.md     # Test documentation
│   │   ├── test_eth_simulateV1.py
│   │   └── manual_test.py
│   ├── docs/
│   │   └── test_report.md
│   ├── configs/
│   │   ├── ec-common/   # Execution client configs
│   │   └── consensus/   # Consensus client configs
│   ├── data/            # Chain data (gitignored)
│   └── logs/            # Container logs (gitignored)
└── README.md           # This file
```

## Quick Start

### 1. Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.12+ (optional, for tests)
- 8GB+ RAM available

### 2. Setup

```bash
cd local-network
./scripts/setup.sh
```

This will:
- Check prerequisites
- Install Python dependencies
- Generate genesis configuration
- Create data directories
- Pull Docker images

### 3. Start Network

```bash
./scripts/start.sh
```

Wait 2-3 minutes for initialization.

### 4. Health Check

```bash
python3 scripts/health_check.py
```

### 5. Run Tests

```bash
python3 tests/test_eth_simulateV1.py
```

## Architecture

### Network Topology

```
                ┌─────────────────────────────┐
                │   eth_testnet Network        │
                └─────────────────────────────┘
                          │         │
          ┌───────────────┘         └───────────────┐
          │                                       │
    ┌─────▼─────┐                           ┌─────▼─────┐
    │ Lighthouse│                           │   Prysm   │
    │  (CC-1)   │                           │  (CC-2)   │
    └─────┬─────┘                           └─────┬─────┘
          │                                       │
          │                                       │
    ┌─────▼─────┐                           ┌─────▼─────┐
    │ op-geth   │                           │  op-reth  │
    │  (EC-1)   │                           │  (EC-2)   │
    │ Standard  │                           │simulateV1 │
    └───────────┘                           └───────────┘
          │                                       │
          └──────────────┬────────────────────────┘
                         │
                  ┌──────▼──────┐
                  │  Validator  │
                  │   (LH VC)   │
                  └─────────────┘
```

### Component Details

#### Execution Clients

**op-geth (Standard)**
- Image: `ghcr.io/unitsnetwork/op-geth:v1.101603.0-1`
- RPC: `http://127.0.0.1:18545`
- Does NOT support eth_simulateV1

**op-reth (Modified)**
- Image: `ghcr.io/unitsnetwork/op-reth:simulate-v1-1.0.0`
- RPC: `http://127.0.0.1:28545`
- DOES support eth_simulateV1

#### Consensus Clients

**Lighthouse**
- Image: `sigp/lighthouse:v5.2.1`
- Connected to: op-geth
- API: `http://127.0.0.1:15052`

**Prysm**
- Image: `gcr.io/prysmaticlabs/prysm/beacon-chain:v5.1.0`
- Connected to: op-reth
- API: `http://127.0.0.1:14000`

## Testing eth_simulateV1

### Basic Example

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

### Python Test Suite

The project includes a comprehensive test suite:

```bash
# Run all tests
python3 tests/test_eth_simulateV1.py

# Run manual interactive tests
python3 tests/manual_test.py

# Run health check
python3 scripts/health_check.py
```

## Pre-funded Accounts

The genesis includes two pre-funded accounts:

**Account 1**
- Address: `0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73`
- Balance: 10,000 ETH
- Private Key: `0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63`

**Account 2**
- Address: `0xf17f52151EbEF6C7334FAD080c5704D77216b732`
- Balance: 10,000 ETH + 1 wei
- Private Key: `0xae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f`

## Test Results

Comprehensive test results are documented in `local-network/docs/test_report.md`.

### Summary

- ✅ Network initialization: PASSED
- ✅ RPC endpoints: PASSED
- ✅ eth_simulateV1 availability: PASSED (op-reth only)
- ✅ Basic simulation: PASSED
- ✅ Depository transactions: PASSED
- ✅ Edge cases: PASSED
- ✅ Block production: PASSED
- ✅ Synchronization: PASSED

**Overall Status**: ✅ READY FOR USE

## Configuration

### Chain Parameters

- Chain ID: 1337
- Slot Time: 12 seconds
- Epoch Duration: 32 slots (6.4 minutes)
- Validator Count: 4
- Terminal Total Difficulty: 0 (Proof-of-Stake)

### Customization

Edit the following files to customize the setup:

- `local-network/docker-compose.yml` - Service configuration
- `local-network/configs/ec-common/genesis.json` - Genesis parameters
- `local-network/configs/consensus/` - Consensus configuration

## Troubleshooting

### Common Issues

**Containers won't start**
```bash
# Check logs
docker compose logs

# Restart network
docker compose restart
```

**eth_simulateV1 not available**
```bash
# Verify op-reth is running
docker ps | grep op-reth

# Check logs
docker compose logs ec-opreth
```

**No blocks being produced**
```bash
# Check validator logs
docker compose logs validator-lighthouse

# Wait for sync
sleep 120
```

For more troubleshooting, see `local-network/README.md`.

## Scripts Reference

### setup.sh
One-time setup script that:
- Checks prerequisites
- Installs dependencies
- Generates genesis
- Pulls images

### start.sh
Starts the entire network with all services.

### stop.sh
Stops all services without removing data.

### health_check.py
Comprehensive health check for:
- Container status
- RPC endpoints
- eth_simulateV1 support
- Block production
- Log errors

### generate-genesis.sh
Generates:
- Consensus genesis state
- Validator keys
- Deposit data
- Configuration files

## Documentation

- **Setup Guide**: `local-network/README.md`
- **Test Documentation**: `local-network/tests/README.md`
- **Test Report**: `local-network/docs/test_report.md`
- **Configuration**: `local-network/.env.example`

## Support

For issues:
1. Check logs: `docker compose logs -f`
2. Run health check: `python3 scripts/health_check.py`
3. Review documentation in `local-network/`

## License

This setup is provided as-is for testing and development purposes.

## Contributing

To add new features or fix issues:

1. Create a branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## Related Projects

- **op-geth**: https://github.com/ethereum-optimism/op-geth
- **op-reth**: https://github.com/paradigmxyz/reth
- **Lighthouse**: https://github.com/sigp/lighthouse
- **Prysm**: https://github.com/prysmaticlabs/prysm

---

**Last Updated**: 2025-01-06
**Version**: 1.0.0
**Branch**: feat-integ-eth-simulatev1-localnet-2cons-2exec
