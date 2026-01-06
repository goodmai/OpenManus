#!/usr/bin/env python3
"""
Health check script for the eth_simulateV1 test network
Checks status of all containers and services
"""

import subprocess
import sys
import time
from typing import Dict, List


def run_command(cmd: List[str]) -> tuple:
    """Run a shell command and return output and return code"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return "", -1
    except Exception as e:
        return f"Error: {str(e)}", -1


def check_docker_containers() -> Dict[str, bool]:
    """Check if all containers are running"""
    print("\n" + "=" * 60)
    print("Checking Docker Containers")
    print("=" * 60)

    containers = {
        "ec-opgeth": False,
        "ec-opreth": False,
        "cc-lighthouse": False,
        "cc-prysm": False,
        "validator-lighthouse": False,
    }

    output, _ = run_command(["docker", "ps", "--format", "{{.Names}}"])
    running_containers = output.strip().split("\n")

    for container in containers:
        if container in running_containers:
            containers[container] = True
            print(f"  ✓ {container}: Running")
        else:
            print(f"  ✗ {container}: Not running")

    return containers


def check_rpc_endpoint(url: str, name: str) -> bool:
    """Check if RPC endpoint is responding"""
    try:
        import httpx

        client = httpx.Client(timeout=5.0)

        payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}

        response = client.post(url, json=payload, timeout=5.0)
        result = response.json()

        if "error" in result:
            print(f"  ✗ {name}: RPC Error - {result['error']}")
            return False

        if "result" in result:
            block_num = int(result["result"], 16)
            print(f"  ✓ {name}: OK (block {block_num})")
            return True

        print(f"  ✗ {name}: Invalid response")
        return False

    except Exception as e:
        print(f"  ✗ {name}: Connection failed - {str(e)[:50]}")
        return False


def check_execution_clients() -> Dict[str, bool]:
    """Check execution clients"""
    print("\n" + "=" * 60)
    print("Checking Execution Clients")
    print("=" * 60)

    status = {}

    # Check op-geth
    status["op-geth"] = check_rpc_endpoint("http://127.0.0.1:18545", "op-geth RPC")

    # Check op-reth
    status["op-reth"] = check_rpc_endpoint("http://127.0.0.1:28545", "op-reth RPC")

    return status


def check_consensus_clients() -> Dict[str, bool]:
    """Check consensus clients"""
    print("\n" + "=" * 60)
    print("Checking Consensus Clients")
    print("=" * 60)

    status = {}

    # Check Lighthouse
    status["lighthouse"] = check_rpc_endpoint(
        "http://127.0.0.1:15052", "Lighthouse API"
    )

    # Check Prysm
    status["prysm"] = check_rpc_endpoint("http://127.0.0.1:14000", "Prysm API")

    return status


def check_eth_simulateV1() -> Dict[str, bool]:
    """Check if eth_simulateV1 is available"""
    print("\n" + "=" * 60)
    print("Checking eth_simulateV1 Support")
    print("=" * 60)

    status = {}

    try:
        import httpx

        client = httpx.Client(timeout=5.0)

        # Test on op-reth
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_simulateV1",
                "params": [{"blockNumber": "latest", "transactions": []}],
                "id": 1,
            }

            response = client.post("http://127.0.0.1:28545", json=payload, timeout=5.0)
            result = response.json()

            if "error" in result:
                if "method not found" in result["error"].get("message", "").lower():
                    print(f"  ✗ op-reth: eth_simulateV1 not available")
                    status["op-reth"] = False
                else:
                    print(
                        f"  ⚠ op-reth: eth_simulateV1 available (returned error: {result['error'].get('message', 'unknown')})"
                    )
                    status["op-reth"] = True
            else:
                print(f"  ✓ op-reth: eth_simulateV1 available")
                status["op-reth"] = True

        except Exception as e:
            print(f"  ✗ op-reth: {str(e)[:50]}")
            status["op-reth"] = False

        # Test on op-geth
        try:
            response = client.post("http://127.0.0.1:18545", json=payload, timeout=5.0)
            result = response.json()

            if "error" in result:
                if "method not found" in result["error"].get("message", "").lower():
                    print(f"  ✗ op-geth: eth_simulateV1 not available")
                    status["op-geth"] = False
                else:
                    print(
                        f"  ⚠ op-geth: eth_simulateV1 available (returned error: {result['error'].get('message', 'unknown')})"
                    )
                    status["op-geth"] = True
            else:
                print(f"  ✓ op-geth: eth_simulateV1 available")
                status["op-geth"] = True

        except Exception as e:
            print(f"  ✗ op-geth: {str(e)[:50]}")
            status["op-geth"] = False

        client.close()

    except Exception as e:
        print(f"  ✗ Check failed: {str(e)}")
        status["op-reth"] = False
        status["op-geth"] = False

    return status


def check_block_production() -> bool:
    """Check if blocks are being produced"""
    print("\n" + "=" * 60)
    print("Checking Block Production")
    print("=" * 60)

    try:
        import httpx

        client = httpx.Client(timeout=5.0)

        # Get initial block number
        payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}

        response = client.post("http://127.0.0.1:18545", json=payload)
        initial_block = int(response.json()["result"], 16)
        print(f"  Initial block: {initial_block}")

        # Wait for 15 seconds (more than one slot)
        print("  Waiting 15 seconds for block production...")
        time.sleep(15)

        # Check block number again
        response = client.post("http://127.0.0.1:18545", json=payload)
        final_block = int(response.json()["result"], 16)
        print(f"  Final block: {final_block}")

        blocks_produced = final_block - initial_block

        if blocks_produced > 0:
            print(f"  ✓ {blocks_produced} block(s) produced")
            client.close()
            return True
        else:
            print(f"  ✗ No blocks produced (network may be syncing)")
            client.close()
            return False

    except Exception as e:
        print(f"  ✗ Block production check failed: {str(e)}")
        return False


def check_logs_for_errors() -> Dict[str, List[str]]:
    """Check container logs for errors"""
    print("\n" + "=" * 60)
    print("Checking Logs for Errors")
    print("=" * 60)

    containers = ["ec-opgeth", "ec-opreth", "cc-lighthouse", "cc-prysm"]
    errors = {}

    for container in containers:
        output, _ = run_command(["docker", "logs", "--tail", "50", container])

        error_lines = []
        for line in output.split("\n"):
            line_lower = line.lower()
            if any(
                keyword in line_lower
                for keyword in ["error", "fatal", "panic", "failed"]
            ):
                # Filter out non-critical errors
                if not any(
                    skip in line_lower for skip in ["error reading", "connection reset"]
                ):
                    error_lines.append(line.strip())

        if error_lines:
            print(f"  ⚠ {container}: Found {len(error_lines)} potential error(s)")
            errors[container] = error_lines[:3]  # Show first 3 errors
            for err in errors[container]:
                print(f"    - {err[:80]}...")
        else:
            print(f"  ✓ {container}: No critical errors found")
            errors[container] = []

    return errors


def print_summary(
    containers: Dict[str, bool],
    execution: Dict[str, bool],
    consensus: Dict[str, bool],
    simulatev1: Dict[str, bool],
    block_production: bool,
    logs: Dict[str, List[str]],
) -> int:
    """Print summary and return exit code"""

    print("\n" + "=" * 60)
    print("HEALTH CHECK SUMMARY")
    print("=" * 60)

    all_healthy = True

    # Containers
    all_containers_ok = all(containers.values())
    print(f"\nContainers: {'✓ HEALTHY' if all_containers_ok else '✗ UNHEALTHY'}")
    for name, status in containers.items():
        print(f"  {name}: {'✓' if status else '✗'}")

    # Execution clients
    all_execution_ok = all(execution.values())
    print(f"\nExecution Clients: {'✓ HEALTHY' if all_execution_ok else '✗ UNHEALTHY'}")
    for name, status in execution.items():
        print(f"  {name}: {'✓' if status else '✗'}")

    # Consensus clients
    all_consensus_ok = all(consensus.values())
    print(f"\nConsensus Clients: {'✓ HEALTHY' if all_consensus_ok else '✗ UNHEALTHY'}")
    for name, status in consensus.items():
        print(f"  {name}: {'✓' if status else '✗'}")

    # eth_simulateV1
    print(f"\neth_simulateV1 Support:")
    for name, status in simulatev1.items():
        print(f"  {name}: {'✓ Available' if status else '✗ Not Available'}")

    # Block production
    print(f"\nBlock Production: {'✓ OK' if block_production else '✗ NOT PRODUCING'}")

    # Critical errors
    critical_errors = sum(len(v) for v in logs.values())
    print(
        f"\nCritical Errors: {'✓ None' if critical_errors == 0 else f'✗ {critical_errors} found'}"
    )

    # Overall status
    all_healthy = (
        all_containers_ok
        and all_execution_ok
        and all_consensus_ok
        and block_production
        and critical_errors == 0
    )

    print("\n" + "=" * 60)
    if all_healthy:
        print("✓ NETWORK IS HEALTHY")
    else:
        print("✗ NETWORK HAS ISSUES")
    print("=" * 60 + "\n")

    return 0 if all_healthy else 1


def main():
    """Main health check"""
    print("\n" + "=" * 60)
    print("eth_simulateV1 Network Health Check")
    print("=" * 60)

    # Run all checks
    containers = check_docker_containers()
    execution = check_execution_clients()
    consensus = check_consensus_clients()
    simulatev1 = check_eth_simulateV1()
    block_production = check_block_production()
    logs = check_logs_for_errors()

    # Print summary
    exit_code = print_summary(
        containers, execution, consensus, simulatev1, block_production, logs
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
