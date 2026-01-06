# eth_simulateV1 Test Suite Documentation

## Overview

This test suite validates the `eth_simulateV1` RPC method implementation on both op-geth (standard) and op-reth (modified) execution clients in a local network environment.

## Test Structure

```
tests/
├── test_eth_simulateV1.py      # Main test suite
├── test_block_production.py     # Block production tests
├── test_synchronization.py    # Sync tests between clients
└── test_consensus.py            # Consensus layer tests
```

## Test Categories

### 1. Basic Functionality Tests (`test_eth_simulateV1.py`)

Tests the core functionality of eth_simulateV1:

- **Empty Transaction Simulation**
  - Tests basic call with empty transaction list
  - Validates response structure
  - Checks block number in response

- **Single Transaction Simulation**
  - Simulates simple ETH transfers
  - Validates gas calculation
  - Checks transaction execution

- **Multiple Transaction Simulation**
  - Simulates batched transactions
  - Validates cumulative gas usage
  - Tests transaction ordering

- **Historical Block Simulation**
  - Simulates at specific block numbers
  - Tests state retrieval
  - Validates historical execution

### 2. Depository Transaction Tests

Tests simulation of depository (bridge) transactions:

- **Large Value Deposits**
  - Simulates deposits with large ETH values
  - Tests gas calculation for large transfers
  - Validates state changes

- **Bridge Contract Interactions**
  - Simulates calls to bridge contract
  - Tests complex state transitions
  - Validates contract execution

- **Multi-Depository Scenarios**
  - Simulates multiple concurrent deposits
  - Tests transaction ordering effects
  - Validates cumulative state changes

### 3. Edge Case Tests

Tests error handling and edge cases:

- **Invalid Block Numbers**
  - Tests with future block numbers
  - Tests with non-existent blocks
  - Validates error messages

- **Invalid Transactions**
  - Tests with malformed transactions
  - Tests with insufficient balance
  - Tests with invalid signatures

- **Boundary Conditions**
  - Tests with zero value
  - Tests with maximum gas
  - Tests with no gas limit

### 4. Comparison Tests

Compares results between op-geth and op-reth:

- **Gas Usage Comparison**
  - Validates identical gas calculation
  - Checks for implementation differences
  - Reports any discrepancies

- **State Comparison**
  - Validates identical state transitions
  - Checks storage changes
  - Validates account updates

- **Result Validation**
  - Compares transaction receipts
  - Validates logs output
  - Checks status codes

## Running Tests

### Run All Tests

```bash
cd /home/engine/project/local-network

# Make sure network is running
docker compose ps

# Run from test runner container
docker compose --profile tests up -d test-runner
docker compose exec test-runner python3 /tests/test_eth_simulateV1.py

# Or run from host (requires httpx)
pip install httpx
python3 tests/test_eth_simulateV1.py
```

### Run Specific Test Category

```bash
# Run only basic tests
docker compose exec test-runner python3 -c "
from test_eth_simulateV1 import test_eth_simulateV1_basic
test_eth_simulateV1_basic()
"

# Run only depository tests
docker compose exec test-runner python3 -c "
from test_eth_simulateV1 import test_eth_simulateV1_depository
test_eth_simulateV1_depository()
"

# Run only edge case tests
docker compose exec test-runner python3 -c "
from test_eth_simulateV1 import test_eth_simulateV1_edge_cases
test_eth_simulateV1_edge_cases()
"
```

### Run with Verbose Output

```bash
docker compose exec test-runner python3 /tests/test_eth_simulateV1.py -v
```

## Test Data

### Pre-funded Accounts

- **Account 1**: `0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73` (10,000 ETH)
- **Account 2**: `0xf17f52151EbEF6C7334FAD080c5704D77216b732` (10,000 ETH)

### Bridge Contract

- **Address**: `0x0000000000000000000000000000000000006A7e`
- **Purpose**: Depository and bridge operations

## Test Results Interpretation

### Success Indicators

- ✓ : Test passed successfully
- ⚠ : Test passed with warnings
- ✗ : Test failed

### Common Failures

**"Method not found"**
- eth_simulateV1 is not available on the client
- Expected on op-geth (standard implementation)
- Should NOT appear on op-reth

**"Connection failed"**
- Client container not running
- Network not started
- Port not exposed

**"Invalid block"**
- Block number doesn't exist
- Client still syncing
- Chain reorganization in progress

**"Insufficient balance"**
- Correct error handling
- Test validates proper error messages

## Expected Behavior

### op-geth (Standard)

- May NOT support eth_simulateV1
- Returns "method not found" error
- This is EXPECTED behavior

### op-reth (Modified)

- MUST support eth_simulateV1
- Returns valid simulation results
- Results should match op-geth (if available) for standard transactions
- Additional features for depository transactions

## Test Report Format

After running tests, a report is generated with:

```
====================================================================
eth_simulateV1 Test Suite
====================================================================

Test Category: Basic Functionality
====================================================================
Test 1: Basic simulation (empty transactions)
  ✓ op-reth: Simulation successful
  ✓ op-geth: Simulation successful

Test 2: Simulation with transfer transaction
  ✓ op-reth: Simulation with transfer successful
  ✗ op-geth: Method not found (expected)

Summary:
  Total tests: 10
  Passed: 8
  Failed: 2
  Warnings: 0
====================================================================
```

## Integration with CI/CD

The tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Test eth_simulateV1

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start Network
        run: |
          cd local-network
          ./scripts/start.sh
      - name: Wait for Services
        run: sleep 120
      - name: Run Health Check
        run: python3 local-network/scripts/health_check.py
      - name: Run Tests
        run: python3 local-network/tests/test_eth_simulateV1.py
```

## Extending Tests

### Adding New Test Cases

1. Create a new function in `test_eth_simulateV1.py`:

```python
def test_your_new_test():
    """Description of your test"""
    opreth = EthRPCClient("http://127.0.0.1:28545")

    try:
        # Your test logic here
        result = opreth.eth_simulateV1(your_params)
        # Validate results
        assert result is not None
        print("  ✓ Test passed")
    finally:
        opreth.close()
```

2. Add to `main()` function:

```python
def main():
    test_eth_simulateV1_basic()
    test_your_new_test()  # Add here
```

### Creating Custom Test Files

Create new test files in `tests/` directory:

```python
#!/usr/bin/env python3
"""Your custom tests"""

import sys
sys.path.insert(0, '../tests')

from test_eth_simulateV1 import EthRPCClient

# Your test code here
```

## Troubleshooting Tests

### Tests Fail to Start

1. Check if network is running:
   ```bash
   docker compose ps
   ```

2. Run health check:
   ```bash
   python3 scripts/health_check.py
   ```

3. Check logs:
   ```bash
   docker compose logs ec-opreth
   ```

### Tests Timeout

1. Increase timeout in test code
2. Check if services are syncing
3. Reduce test load

### Inconsistent Results

1. Wait for network to stabilize
2. Check for chain reorganizations
3. Verify both clients are synced

## Best Practices

1. **Always run health check before tests**
2. **Wait for network initialization** (2-3 minutes)
3. **Run tests multiple times** to catch race conditions
4. **Check logs** after failed tests
5. **Document any unexpected behavior**

## Support

For test-related issues:
1. Check test output for error messages
2. Review logs in `logs/` directory
3. Run health check for overall status
4. Consult main README for network issues
