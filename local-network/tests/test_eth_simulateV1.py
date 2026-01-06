#!/usr/bin/env python3
"""
Test script for eth_simulateV1 on op-geth and op-reth
"""

import time
from typing import Any, Dict, List

import httpx


class EthRPCClient:
    """Simple Ethereum RPC client"""

    def __init__(self, url: str):
        self.url = url
        self.client = httpx.Client(timeout=30.0)
        self.request_id = 0

    def _call(self, method: str, params: List[Any] = None) -> Any:
        """Make an RPC call"""
        self.request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": self.request_id,
        }

        response = self.client.post(
            self.url, json=payload, headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            raise Exception(f"RPC Error: {result['error']}")

        return result.get("result")

    def get_block_number(self) -> int:
        """Get current block number"""
        result = self._call("eth_blockNumber")
        return int(result, 16)

    def get_block_by_number(self, number: int, full_txs: bool = False) -> Dict:
        """Get block by number"""
        return self._call("eth_getBlockByNumber", [hex(number), full_txs])

    def eth_simulateV1(self, params: Dict) -> Dict:
        """Call eth_simulateV1 RPC method"""
        return self._call("eth_simulateV1", [params])

    def send_raw_transaction(self, tx_hex: str) -> str:
        """Send raw transaction"""
        return self._call("eth_sendRawTransaction", [tx_hex])

    def get_balance(self, address: str, block: str = "latest") -> int:
        """Get balance of address"""
        result = self._call("eth_getBalance", [address, block])
        return int(result, 16)

    def chain_id(self) -> int:
        """Get chain ID"""
        result = self._call("eth_chainId")
        return int(result, 16)

    def close(self):
        """Close the client"""
        self.client.close()


def test_eth_simulateV1_basic():
    """Test basic eth_simulateV1 functionality"""
    print("\n" + "=" * 60)
    print("Testing eth_simulateV1 - Basic Functionality")
    print("=" * 60)

    # Initialize clients
    opgeth = EthRPCClient("http://127.0.0.1:18545")
    opreth = EthRPCClient("http://127.0.0.1:28545")

    try:
        # Check if clients are ready
        print("\nChecking client connectivity...")
        opgeth_block = opgeth.get_block_number()
        opreth_block = opreth.get_block_number()
        print(f"  op-geth block: {opgeth_block}")
        print(f"  op-reth block: {opreth_block}")

        # Test parameters
        simulation_params = {"blockNumber": "latest", "state": None, "transactions": []}

        # Test 1: Basic simulation with empty transaction list
        print("\nTest 1: Basic simulation (empty transactions)")
        try:
            result = opreth.eth_simulateV1(simulation_params)
            print(f"  ✓ op-reth: Simulation successful")
            print(f"    Block number: {result.get('blockNumber', 'N/A')}")
        except Exception as e:
            print(f"  ✗ op-reth: {str(e)}")

        try:
            result = opgeth.eth_simulateV1(simulation_params)
            print(f"  ✓ op-geth: Simulation successful")
            print(f"    Block number: {result.get('blockNumber', 'N/A')}")
        except Exception as e:
            print(f"  ✗ op-geth: {str(e)} (may not support eth_simulateV1)")

        # Test 2: Simulation with a simple transfer transaction
        print("\nTest 2: Simulation with transfer transaction")

        # Create a simple transfer transaction
        tx_params = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "value": "0xde0b6b3a7640000",  # 1 ETH
            "gas": "0x5208",
            "gasPrice": "0x0",
        }

        simulation_params["transactions"] = [tx_params]

        try:
            result = opreth.eth_simulateV1(simulation_params)
            print(f"  ✓ op-reth: Simulation with transfer successful")
            print(f"    Gas used: {result.get('gasUsed', 'N/A')}")
        except Exception as e:
            print(f"  ✗ op-reth: {str(e)}")

        try:
            result = opgeth.eth_simulateV1(simulation_params)
            print(f"  ✓ op-geth: Simulation with transfer successful")
            print(f"    Gas used: {result.get('gasUsed', 'N/A')}")
        except Exception as e:
            print(f"  ✗ op-geth: {str(e)} (may not support eth_simulateV1)")

        # Test 3: Simulation with block number
        print("\nTest 3: Simulation with specific block number")
        if opgeth_block >= 5:
            block_num = opgeth_block - 5
        else:
            block_num = 0

        simulation_params["blockNumber"] = hex(block_num)

        try:
            result = opreth.eth_simulateV1(simulation_params)
            print(f"  ✓ op-reth: Simulation at block {block_num} successful")
        except Exception as e:
            print(f"  ✗ op-reth: {str(e)}")

        # Test 4: Compare results between clients
        print("\nTest 4: Comparing results between op-geth and op-reth")
        simulation_params["blockNumber"] = "latest"
        simulation_params["transactions"] = [tx_params]

        try:
            reth_result = opreth.eth_simulateV1(simulation_params)
            geth_result = opgeth.eth_simulateV1(simulation_params)

            # Compare gas used
            reth_gas = reth_result.get("gasUsed", "N/A")
            geth_gas = geth_result.get("gasUsed", "N/A")

            if reth_gas == geth_gas:
                print(f"  ✓ Results match: Gas used = {reth_gas}")
            else:
                print(f"  ⚠ Results differ:")
                print(f"    op-reth gas used: {reth_gas}")
                print(f"    op-geth gas used: {geth_gas}")
        except Exception as e:
            print(f"  ✗ Comparison failed: {str(e)}")

        print("\n" + "=" * 60)
        print("Basic tests completed!")
        print("=" * 60)

    finally:
        opgeth.close()
        opreth.close()


def test_eth_simulateV1_depository():
    """Test eth_simulateV1 with depository transactions"""
    print("\n" + "=" * 60)
    print("Testing eth_simulateV1 - Depository Transactions")
    print("=" * 60)

    opreth = EthRPCClient("http://127.0.0.1:28545")

    try:
        # Get current block
        current_block = opreth.get_block_number()
        print(f"\nCurrent block: {current_block}")

        # Get a previous block for context
        if current_block > 10:
            prev_block = opreth.get_block_by_number(current_block - 10, True)
            print(
                f"Previous block ({current_block - 10}) has {len(prev_block.get('transactions', []))} transactions"
            )

        # Test simulation with depository-style transaction
        # This simulates a deposit to the bridge contract
        deposit_tx = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0x0000000000000000000000000000000000006A7e",  # Bridge contract
            "value": "0xbc614e0000000",  # 1.3 ETH (large deposit)
            "gas": "0x186a0",  # 100,000 gas
            "gasPrice": "0x1",
        }

        simulation_params = {"blockNumber": "latest", "transactions": [deposit_tx]}

        print("\nSimulating depository transaction...")
        try:
            result = opreth.eth_simulateV1(simulation_params)
            print(f"  ✓ Simulation successful")
            print(f"    Gas used: {result.get('gasUsed', 'N/A')}")
            print(f"    Status: {result.get('status', 'N/A')}")
        except Exception as e:
            print(f"  ✗ Simulation failed: {str(e)}")

        # Test multiple transactions
        print("\nSimulating multiple transactions...")
        tx1 = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "value": "0xde0b6b3a7640000",
            "gas": "0x5208",
            "gasPrice": "0x1",
        }
        tx2 = {
            "from": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "to": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "value": "0x56bc75e2d63100000",  # 100 ETH
            "gas": "0x5208",
            "gasPrice": "0x1",
        }

        simulation_params["transactions"] = [tx1, tx2]

        try:
            result = opreth.eth_simulateV1(simulation_params)
            print(f"  ✓ Multi-transaction simulation successful")
            print(f"    Total gas used: {result.get('gasUsed', 'N/A')}")
        except Exception as e:
            print(f"  ✗ Multi-transaction simulation failed: {str(e)}")

        print("\n" + "=" * 60)
        print("Depository tests completed!")
        print("=" * 60)

    finally:
        opreth.close()


def test_eth_simulateV1_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "=" * 60)
    print("Testing eth_simulateV1 - Edge Cases")
    print("=" * 60)

    opreth = EthRPCClient("http://127.0.0.1:28545")

    try:
        # Test 1: Invalid block number
        print("\nTest 1: Invalid block number")
        try:
            result = opreth.eth_simulateV1(
                {"blockNumber": "0xFFFFFFFFFFFFFFFF", "transactions": []}
            )
            print(f"  ⚠ Should have failed but succeeded")
        except Exception as e:
            print(f"  ✓ Correctly rejected invalid block: {str(e)[:50]}...")

        # Test 2: Missing required fields
        print("\nTest 2: Missing required fields")
        try:
            result = opreth.eth_simulateV1({"blockNumber": "latest"})
            print(f"  ⚠ Should have failed but succeeded")
        except Exception as e:
            print(f"  ✓ Correctly rejected missing fields: {str(e)[:50]}...")

        # Test 3: Invalid transaction format
        print("\nTest 3: Invalid transaction format")
        try:
            result = opreth.eth_simulateV1(
                {"blockNumber": "latest", "transactions": [{"from": "0xinvalid"}]}
            )
            print(f"  ⚠ Should have failed but succeeded")
        except Exception as e:
            print(f"  ✓ Correctly rejected invalid tx: {str(e)[:50]}...")

        # Test 4: Insufficient balance
        print("\nTest 4: Transaction with insufficient balance")
        insufficient_tx = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "value": "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",  # Huge amount
            "gas": "0x5208",
            "gasPrice": "0x1",
        }

        try:
            result = opreth.eth_simulateV1(
                {"blockNumber": "latest", "transactions": [insufficient_tx]}
            )
            print(f"  ⚠ Should have failed but succeeded")
        except Exception as e:
            print(f"  ✓ Correctly rejected insufficient balance: {str(e)[:50]}...")

        # Test 5: Zero value transaction
        print("\nTest 5: Zero value transaction")
        zero_tx = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "value": "0x0",
            "gas": "0x5208",
            "gasPrice": "0x0",
        }

        try:
            result = opreth.eth_simulateV1(
                {"blockNumber": "latest", "transactions": [zero_tx]}
            )
            print(f"  ✓ Zero value transaction simulated successfully")
            print(f"    Gas used: {result.get('gasUsed', 'N/A')}")
        except Exception as e:
            print(f"  ✗ Zero value transaction failed: {str(e)}")

        print("\n" + "=" * 60)
        print("Edge case tests completed!")
        print("=" * 60)

    finally:
        opreth.close()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("eth_simulateV1 Test Suite")
    print("=" * 60)

    # Wait for services to be ready
    print("\nWaiting for services to be ready...")
    time.sleep(5)

    # Run tests
    test_eth_simulateV1_basic()
    test_eth_simulateV1_depository()
    test_eth_simulateV1_edge_cases()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
