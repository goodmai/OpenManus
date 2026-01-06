#!/usr/bin/env python3
"""
Test script for eth_simulateV1 on both op-geth and op-reth execution clients.
Verifies that both clients return identical results.
"""
import asyncio
import json
import time
from typing import Dict, List, Tuple
from web3 import Web3
from eth_account import Account

class ETHSimulateV1Tester:
    def __init__(self):
        self.op_geth_url = "http://127.0.0.1:18545"
        self.op_reth_url = "http://127.0.0.1:38545"
        self.op_geth_w3 = Web3(Web3.HTTPProvider(self.op_geth_url))
        self.op_reth_w3 = Web3(Web3.HTTPProvider(self.op_reth_url))
        
        # Test accounts
        self.test_account = Account.from_key(
            "0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63"
        )
        
    def check_connection(self) -> Tuple[bool, bool]:
        """Check connection to both execution clients"""
        geth_connected = self.op_geth_w3.is_connected()
        reth_connected = self.op_reth_w3.is_connected()
        return geth_connected, reth_connected
    
    def get_block_number(self, w3: Web3) -> int:
        """Get latest block number"""
        try:
            return w3.eth.block_number
        except Exception as e:
            print(f"Error getting block number: {e}")
            return -1
    
    def test_eth_simulateV1_exists(self, w3: Web3, client_name: str) -> bool:
        """Test if eth_simulateV1 method exists"""
        try:
            # Try to call eth_simulateV1 with minimal params
            result = w3.provider.make_request(
                "eth_simulateV1", 
                [{"pendingTransactions": []}]
            )
            print(f"✓ {client_name}: eth_simulateV1 method exists")
            return True
        except Exception as e:
            print(f"✗ {client_name}: eth_simulateV1 method not available: {e}")
            return False
    
    def test_basic_simulation(self, w3: Web3, client_name: str) -> Dict:
        """Test basic eth_simulateV1 call"""
        try:
            params = {
                "pendingTransactions": [],
                "blockTimestamp": int(time.time()),
                "blockNumber": self.get_block_number(w3) + 1
            }
            result = w3.provider.make_request("eth_simulateV1", [params])
            print(f"✓ {client_name}: Basic simulation successful")
            return result
        except Exception as e:
            print(f"✗ {client_name}: Basic simulation failed: {e}")
            return {"error": str(e)}
    
    def test_with_transaction(self, w3: Web3, client_name: str) -> Dict:
        """Test eth_simulateV1 with a transaction"""
        try:
            # Get latest block to use as base
            latest_block = self.op_geth_w3.eth.get_block('latest')
            next_block_number = latest_block['number'] + 1
            
            # Create a simple value transfer transaction
            to_address = "0xf17f52151EbEF6C7334FAD080c5704D77216b732"
            
            tx = {
                'to': to_address,
                'value': 1000,
                'gas': 21000,
                'maxFeePerGas': self.op_geth_w3.eth.gas_price,
                'maxPriorityFeePerGas': self.op_geth_w3.eth.max_priority_fee_per_gas or 1000000000,
                'nonce': self.op_geth_w3.eth.get_transaction_count(self.test_account.address),
            }
            
            # Sign transaction
            signed_tx = self.op_geth_w3.eth.account.sign_transaction(tx, self.test_account.key)
            
            params = {
                "pendingTransactions": [signed_tx.rawTransaction.hex()],
                "blockTimestamp": int(time.time()) + 12,
                "blockNumber": next_block_number
            }
            
            result = w3.provider.make_request("eth_simulateV1", [params])
            print(f"✓ {client_name}: Transaction simulation successful")
            return result
        except Exception as e:
            print(f"✗ {client_name}: Transaction simulation failed: {e}")
            return {"error": str(e)}
    
    def test_depository_simulation(self, w3: Web3, client_name: str) -> Dict:
        """Test eth_simulateV1 with depository-related transactions"""
        try:
            # Create multiple transactions to simulate depository activity
            latest_block = self.op_geth_w3.eth.get_block('latest')
            next_block_number = latest_block['number'] + 1
            
            # Transaction 1: Deposit
            deposit_tx = {
                'to': "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
                'value': 100000,
                'gas': 21000,
                'maxFeePerGas': self.op_geth_w3.eth.gas_price,
                'maxPriorityFeePerGas': self.op_geth_w3.eth.max_priority_fee_per_gas or 1000000000,
                'nonce': self.op_geth_w3.eth.get_transaction_count(self.test_account.address),
            }
            
            signed_deposit = self.op_geth_w3.eth.account.sign_transaction(deposit_tx, self.test_account.key)
            
            params = {
                "pendingTransactions": [signed_deposit.rawTransaction.hex()],
                "blockTimestamp": int(time.time()) + 12,
                "blockNumber": next_block_number
            }
            
            result = w3.provider.make_request("eth_simulateV1", [params])
            print(f"✓ {client_name}: Depository simulation successful")
            return result
        except Exception as e:
            print(f"✗ {client_name}: Depository simulation failed: {e}")
            return {"error": str(e)}
    
    def compare_results(self, geth_result: Dict, reth_result: Dict) -> bool:
        """Compare results from both clients"""
        # Normalize results for comparison
        def normalize(result):
            if 'error' in result:
                return {'error': result['error']}
            # Convert to JSON-serializable format
            return json.loads(json.dumps(result, default=str))
        
        normalized_geth = normalize(geth_result)
        normalized_reth = normalize(reth_result)
        
        if normalized_geth == normalized_reth:
            print("✓ Results from op-geth and op-reth are IDENTICAL")
            return True
        else:
            print("✗ Results from op-geth and op-reth are DIFFERENT")
            print(f"op-geth result: {json.dumps(normalized_geth, indent=2)}")
            print(f"op-reth result: {json.dumps(normalized_reth, indent=2)}")
            return False
    
    def check_block_production(self) -> Dict:
        """Check block production on both clients"""
        geth_block = self.get_block_number(self.op_geth_w3)
        reth_block = self.get_block_number(self.op_reth_w3)
        
        return {
            "op-geth": geth_block,
            "op-reth": reth_block,
            "in_sync": abs(geth_block - reth_block) <= 1
        }
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("ETH_SIMULATEV1 TESTING")
        print("=" * 80)
        
        # Check connections
        print("\n1. Checking connections...")
        geth_connected, reth_connected = self.check_connection()
        print(f"   op-geth: {'✓ Connected' if geth_connected else '✗ Not connected'}")
        print(f"   op-reth: {'✓ Connected' if reth_connected else '✗ Not connected'}")
        
        if not (geth_connected and reth_connected):
            print("ERROR: Cannot connect to both execution clients")
            return False
        
        # Check block production
        print("\n2. Checking block production...")
        block_status = self.check_block_production()
        print(f"   op-geth block: {block_status['op-geth']}")
        print(f"   op-reth block: {block_status['op-reth']}")
        print(f"   In sync: {'✓ Yes' if block_status['in_sync'] else '✗ No'}")
        
        # Test eth_simulateV1 existence
        print("\n3. Testing eth_simulateV1 method existence...")
        geth_exists = self.test_eth_simulateV1_exists(self.op_geth_w3, "op-geth")
        reth_exists = self.test_eth_simulateV1_exists(self.op_reth_w3, "op-reth")
        
        if not (geth_exists and reth_exists):
            print("ERROR: eth_simulateV1 not available on one or both clients")
            return False
        
        # Test basic simulation
        print("\n4. Testing basic simulation...")
        geth_basic = self.test_basic_simulation(self.op_geth_w3, "op-geth")
        reth_basic = self.test_basic_simulation(self.op_reth_w3, "op-reth")
        basic_match = self.compare_results(geth_basic, reth_basic)
        
        # Test with transaction
        print("\n5. Testing with transaction...")
        geth_tx = self.test_with_transaction(self.op_geth_w3, "op-geth")
        reth_tx = self.test_with_transaction(self.op_reth_w3, "op-reth")
        tx_match = self.compare_results(geth_tx, reth_tx)
        
        # Test depository simulation
        print("\n6. Testing depository simulation...")
        geth_dep = self.test_depository_simulation(self.op_geth_w3, "op-geth")
        reth_dep = self.test_depository_simulation(self.op_reth_w3, "op-reth")
        dep_match = self.compare_results(geth_dep, reth_dep)
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Connections: {'✓' if geth_connected and reth_connected else '✗'}")
        print(f"Block sync: {'✓' if block_status['in_sync'] else '✗'}")
        print(f"eth_simulateV1 exists: {'✓' if geth_exists and reth_exists else '✗'}")
        print(f"Basic simulation match: {'✓' if basic_match else '✗'}")
        print(f"Transaction simulation match: {'✓' if tx_match else '✗'}")
        print(f"Depository simulation match: {'✓' if dep_match else '✗'}")
        
        all_passed = all([
            geth_connected, reth_connected, 
            block_status['in_sync'],
            geth_exists, reth_exists,
            basic_match, tx_match, dep_match
        ])
        
        print("\n" + ("=" * 80))
        if all_passed:
            print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        else:
            print("✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("=" * 80)
        
        return all_passed

if __name__ == "__main__":
    tester = ETHSimulateV1Tester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
