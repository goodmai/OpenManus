#!/usr/bin/env python3
"""
Manual testing examples for eth_simulateV1
This script demonstrates various ways to test eth_simulateV1
"""

import json
import time

import httpx


class ManualTester:
    """Manual testing utilities for eth_simulateV1"""

    def __init__(
        self, opgeth_url="http://127.0.0.1:18545", opreth_url="http://127.0.0.1:28545"
    ):
        self.opgeth_url = opgeth_url
        self.opreth_url = opreth_url
        self.client = httpx.Client(timeout=30.0)

    def rpc_call(self, url, method, params=None):
        """Make an RPC call"""
        payload = {"jsonrpc": "2.0", "method": method, "params": params or [], "id": 1}

        try:
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def print_result(self, title, result):
        """Pretty print a result"""
        print(f"\n{title}")
        print("=" * 60)
        print(json.dumps(result, indent=2))

    def test_1_basic_call(self):
        """Test 1: Basic eth_simulateV1 call with empty transactions"""
        print("\n" + "=" * 60)
        print("TEST 1: Basic Call (Empty Transactions)")
        print("=" * 60)

        params = {"blockNumber": "latest", "transactions": []}

        result = self.rpc_call(self.opreth_url, "eth_simulateV1", [params])

        self.print_result("Result:", result)
        return result

    def test_2_simple_transfer(self):
        """Test 2: Simple ETH transfer"""
        print("\n" + "=" * 60)
        print("TEST 2: Simple ETH Transfer")
        print("=" * 60)

        tx = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "value": "0xde0b6b3a7640000",  # 1 ETH
            "gas": "0x5208",
            "gasPrice": "0x0",
        }

        params = {"blockNumber": "latest", "transactions": [tx]}

        result = self.rpc_call(self.opreth_url, "eth_simulateV1", [params])

        self.print_result("Result:", result)
        return result

    def test_3_zero_value(self):
        """Test 3: Zero value transfer"""
        print("\n" + "=" * 60)
        print("TEST 3: Zero Value Transfer")
        print("=" * 60)

        tx = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "value": "0x0",
            "gas": "0x5208",
            "gasPrice": "0x0",
        }

        params = {"blockNumber": "latest", "transactions": [tx]}

        result = self.rpc_call(self.opreth_url, "eth_simulateV1", [params])

        self.print_result("Result:", result)
        return result

    def test_4_multiple_transfers(self):
        """Test 4: Multiple transfers in one simulation"""
        print("\n" + "=" * 60)
        print("TEST 4: Multiple Transfers")
        print("=" * 60)

        tx1 = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "value": "0xde0b6b3a7640000",
            "gas": "0x5208",
            "gasPrice": "0x0",
        }

        tx2 = {
            "from": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "to": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "value": "0x56bc75e2d63100000",  # 100 ETH
            "gas": "0x5208",
            "gasPrice": "0x0",
        }

        params = {"blockNumber": "latest", "transactions": [tx1, tx2]}

        result = self.rpc_call(self.opreth_url, "eth_simulateV1", [params])

        self.print_result("Result:", result)
        return result

    def test_5_large_value_deposit(self):
        """Test 5: Large value depository transaction"""
        print("\n" + "=" * 60)
        print("TEST 5: Large Value Deposit to Bridge")
        print("=" * 60)

        tx = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0x0000000000000000000000000000000000006A7e",  # Bridge contract
            "value": "0xbc614e0000000",  # 1.3 ETH
            "gas": "0x186a0",  # 100,000
            "gasPrice": "0x1",
        }

        params = {"blockNumber": "latest", "transactions": [tx]}

        result = self.rpc_call(self.opreth_url, "eth_simulateV1", [params])

        self.print_result("Result:", result)
        return result

    def test_6_historical_block(self):
        """Test 6: Simulation at historical block"""
        print("\n" + "=" * 60)
        print("TEST 6: Historical Block Simulation")
        print("=" * 60)

        # Get current block number
        block_result = self.rpc_call(self.opreth_url, "eth_blockNumber")
        if "error" in block_result:
            print("ERROR: Could not get current block number")
            return

        current_block = int(block_result["result"], 16)
        print(f"Current block: {current_block}")

        if current_block > 5:
            target_block = current_block - 5
        else:
            target_block = 0

        print(f"Simulating at block: {target_block}")

        tx = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "value": "0xde0b6b3a7640000",
            "gas": "0x5208",
            "gasPrice": "0x0",
        }

        params = {"blockNumber": hex(target_block), "transactions": [tx]}

        result = self.rpc_call(self.opreth_url, "eth_simulateV1", [params])

        self.print_result("Result:", result)
        return result

    def test_7_insufficient_balance(self):
        """Test 7: Transaction with insufficient balance"""
        print("\n" + "=" * 60)
        print("TEST 7: Insufficient Balance (Expected Error)")
        print("=" * 60)

        tx = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "value": "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            "gas": "0x5208",
            "gasPrice": "0x1",
        }

        params = {"blockNumber": "latest", "transactions": [tx]}

        result = self.rpc_call(self.opreth_url, "eth_simulateV1", [params])

        self.print_result("Result:", result)
        return result

    def test_8_get_balance(self):
        """Test 8: Get balance of pre-funded accounts"""
        print("\n" + "=" * 60)
        print("TEST 8: Get Balance of Pre-funded Accounts")
        print("=" * 60)

        accounts = [
            "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
        ]

        for account in accounts:
            result = self.rpc_call(
                self.opreth_url, "eth_getBalance", [account, "latest"]
            )
            if "result" in result:
                balance_wei = int(result["result"], 16)
                balance_eth = balance_wei / 10**18
                print(f"{account}: {balance_eth:.4f} ETH ({balance_wei} wei)")
            else:
                print(f"{account}: ERROR - {result.get('error', 'Unknown')}")

    def test_9_compare_clients(self):
        """Test 9: Compare op-geth and op-reth"""
        print("\n" + "=" * 60)
        print("TEST 9: Compare op-geth and op-reth")
        print("=" * 60)

        tx = {
            "from": "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73",
            "to": "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
            "value": "0xde0b6b3a7640000",
            "gas": "0x5208",
            "gasPrice": "0x0",
        }

        params = {"blockNumber": "latest", "transactions": [tx]}

        print("\nop-reth result:")
        reth_result = self.rpc_call(self.opreth_url, "eth_simulateV1", [params])
        print(json.dumps(reth_result, indent=2))

        print("\nop-geth result:")
        geth_result = self.rpc_call(self.opgeth_url, "eth_simulateV1", [params])
        print(json.dumps(geth_result, indent=2))

        return {"reth": reth_result, "geth": geth_result}

    def test_10_get_block_info(self):
        """Test 10: Get current block information"""
        print("\n" + "=" * 60)
        print("TEST 10: Get Current Block Information")
        print("=" * 60)

        # Get block number
        block_num_result = self.rpc_call(self.opreth_url, "eth_blockNumber")
        if "result" in block_num_result:
            block_num = int(block_num_result["result"], 16)
            print(f"Block Number: {block_num}")
        else:
            print("ERROR: Could not get block number")
            return

        # Get block details
        block_result = self.rpc_call(
            self.opreth_url, "eth_getBlockByNumber", ["latest", False]
        )

        if "result" in block_result:
            block = block_result["result"]
            print(f"\nBlock Hash: {block['hash']}")
            print(f"Parent Hash: {block['parentHash']}")
            print(f"Timestamp: {int(block['timestamp'], 16)}")
            print(f"Number of Transactions: {len(block.get('transactions', []))}")
            print(f"Gas Used: {int(block['gasUsed'], 16)}")
            print(f"Gas Limit: {int(block['gasLimit'], 16)}")
        else:
            print("ERROR: Could not get block details")

    def run_all_tests(self):
        """Run all manual tests"""
        print("\n" + "=" * 60)
        print("RUNNING ALL MANUAL TESTS")
        print("=" * 60)

        results = {}

        try:
            results["test_1"] = self.test_1_basic_call()
            time.sleep(1)

            results["test_2"] = self.test_2_simple_transfer()
            time.sleep(1)

            results["test_3"] = self.test_3_zero_value()
            time.sleep(1)

            results["test_4"] = self.test_4_multiple_transfers()
            time.sleep(1)

            results["test_5"] = self.test_5_large_value_deposit()
            time.sleep(1)

            results["test_6"] = self.test_6_historical_block()
            time.sleep(1)

            results["test_7"] = self.test_7_insufficient_balance()
            time.sleep(1)

            self.test_8_get_balance()
            time.sleep(1)

            results["test_9"] = self.test_9_compare_clients()
            time.sleep(1)

            self.test_10_get_block_info()

        except Exception as e:
            print(f"\nERROR: {str(e)}")
            import traceback

            traceback.print_exc()

        finally:
            self.client.close()

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)

        return results


def main():
    """Main function"""
    print("=" * 60)
    print("eth_simulateV1 Manual Testing")
    print("=" * 60)

    tester = ManualTester()

    # Run all tests
    tester.run_all_tests()

    # Ask if user wants to run specific tests
    print("\n" + "=" * 60)
    print("Would you like to run specific tests?")
    print("Available tests:")
    print("  1 - Basic call")
    print("  2 - Simple transfer")
    print("  3 - Zero value")
    print("  4 - Multiple transfers")
    print("  5 - Large deposit")
    print("  6 - Historical block")
    print("  7 - Insufficient balance")
    print("  8 - Get balances")
    print("  9 - Compare clients")
    print("  10 - Block info")
    print("  0 - Exit")
    print("=" * 60)

    while True:
        try:
            choice = input("\nEnter test number (0 to exit): ").strip()

            if choice == "0":
                print("Exiting...")
                break
            elif choice == "1":
                tester.test_1_basic_call()
            elif choice == "2":
                tester.test_2_simple_transfer()
            elif choice == "3":
                tester.test_3_zero_value()
            elif choice == "4":
                tester.test_4_multiple_transfers()
            elif choice == "5":
                tester.test_5_large_value_deposit()
            elif choice == "6":
                tester.test_6_historical_block()
            elif choice == "7":
                tester.test_7_insufficient_balance()
            elif choice == "8":
                tester.test_8_get_balance()
            elif choice == "9":
                tester.test_9_compare_clients()
            elif choice == "10":
                tester.test_10_get_block_info()
            else:
                print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
