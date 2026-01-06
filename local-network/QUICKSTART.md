# eth_simulateV1 Local Network - Quick Start Guide

## Overview

This guide provides quick instructions to set up and test `eth_simulateV1` RPC method in a local Ethereum network with 2 consensus clients and 2 execution clients.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.12+ (for tests)
- 8GB+ RAM available

## 5-Minute Setup

### 1. Navigate to Project Directory

```bash
cd /home/engine/project/local-network
```

### 2. Run Setup Script

```bash
./scripts/setup.sh
```

This will:
- Check prerequisites
- Install Python dependencies
- Generate genesis configuration
- Create data directories
- Pull Docker images

### 3. Start the Network

```bash
./scripts/start.sh
```

Wait 2-3 minutes for all services to initialize.

### 4. Verify Health

```bash
python3 scripts/health_check.py
```

You should see all services marked as healthy.

### 5. Run Tests

```bash
python3 tests/test_eth_simulateV1.py
```

This will run comprehensive tests on `eth_simulateV1`.

## Testing eth_simulateV1

### Quick Test

```bash
# Test with curl
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

### Python Test

```python
import httpx

client = httpx.Client()

response = client.post(
    "http://127.0.0.1:28545",
    json={
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
    }
)

print(response.json())
```

## API Endpoints

| Service | Endpoint | Purpose |
|---------|----------|---------|
| op-geth RPC | http://127.0.0.1:18545 | Standard execution client |
| op-reth RPC | http://127.0.0.1:28545 | Modified client with eth_simulateV1 |
| Lighthouse API | http://127.0.0.1:15052 | Consensus client API |
| Prysm API | http://127.0.0.1:14000 | Consensus client API |

**Note**: Only op-reth (port 28545) supports `eth_simulateV1`.

## Pre-funded Accounts

Use these accounts for testing:

**Account 1**
- Address: `0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73`
- Balance: 10,000 ETH
- Private Key: `0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63`

**Account 2**
- Address: `0xf17f52151EbEF6C7334FAD080c5704D77216b732`
- Balance: 10,000 ETH + 1 wei
- Private Key: `0xae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f`

## Common Commands

### View Logs

```bash
# All logs
docker compose logs -f

# Specific service
docker compose logs -f ec-opreth

# Last 100 lines
docker compose logs --tail=100
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart ec-opreth
```

### Stop Network

```bash
./scripts/stop.sh
```

### Clean Everything

```bash
docker compose down -v
rm -rf data/*
```

## Troubleshooting

### Network Not Starting

```bash
# Check Docker status
docker ps

# Check logs
docker compose logs

# Restart Docker daemon
sudo systemctl restart docker
```

### eth_simulateV1 Not Working

```bash
# Check op-reth container
docker ps | grep op-reth

# Check logs
docker compose logs ec-opreth

# Verify RPC endpoint
curl http://127.0.0.1:28545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

### No Blocks Produced

```bash
# Wait longer (need at least 12 seconds per block)
sleep 30

# Check validator logs
docker compose logs validator-lighthouse

# Check consensus client logs
docker compose logs cc-lighthouse
```

## Advanced Usage

### Manual Testing

```bash
python3 tests/manual_test.py
```

This provides an interactive menu for testing various scenarios.

### Custom Configuration

Edit `docker-compose.yml` to customize:
- Port mappings
- Resource limits
- Environment variables
- Volume mounts

### Add More Validators

Edit `configs/consensus/deposit-data.json` and regenerate:
```bash
./scripts/stop.sh
rm -rf data/*
./scripts/generate-genesis.sh
./scripts/start.sh
```

## Documentation

- **Detailed Guide**: `README.md`
- **Test Documentation**: `tests/README.md`
- **Test Report**: `docs/test_report.md`
- **Configuration**: `.env.example`

## Expected Behavior

- ✅ op-reth (port 28545): Supports `eth_simulateV1`
- ✅ op-geth (port 18545): Does NOT support `eth_simulateV1` (returns "method not found")
- ✅ Blocks produced every ~12 seconds
- ✅ All containers healthy
- ✅ Tests pass successfully

## Support

For detailed information:
1. Read `README.md`
2. Check `tests/README.md`
3. Review `docs/test_report.md`
4. Run `python3 scripts/health_check.py`

## Next Steps

1. ✅ Complete initial setup
2. ✅ Run health check
3. ✅ Run test suite
4. ✅ Try manual testing
5. ✅ Explore custom transactions
6. ✅ Build your own applications

---

**Version**: 1.0.0
**Last Updated**: 2025-01-06
