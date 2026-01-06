#!/usr/bin/env python3
"""
eth_simulateV1 Proxy Service

This service implements eth_simulateV1 RPC method by using eth_call under the hood.
It acts as a translation layer between eth_simulateV1 requests and eth_call responses.
"""

import json
from typing import Any, Dict, List

from flask import Flask, jsonify, request
from flask_cors import CORS
from web3 import Web3


app = Flask(__name__)
CORS(app)

# Configuration
GETH_RPC_URL = "http://ec-1:8545"
RETH_RPC_URL = "http://127.0.0.1:8545"  # This service runs inside container
DEFAULT_BACKEND = GETH_RPC_URL

# Initialize Web3 connections
w3_geth = Web3(Web3.HTTPProvider(GETH_RPC_URL))

# Cache for simulation results
simulation_cache = {}


def parse_hex_to_int(hex_str: str) -> int:
    """Parse hex string to int"""
    if hex_str is None or hex_str == "0x":
        return 0
    return int(hex_str, 16)


def int_to_hex(num: int) -> str:
    """Convert int to hex string"""
    return hex(num)


def call_backend(method: str, params: List[Any], backend_url: str = None) -> Any:
    """Call backend RPC method"""
    if backend_url is None:
        backend_url = DEFAULT_BACKEND

    try:
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}

        response = Web3.HTTPProvider(backend_url).make_request(
            json.dumps(payload).encode("utf-8"), {}
        )

        if "result" in response:
            return response["result"]
        elif "error" in response:
            raise Exception(f"RPC Error: {response['error']}")
        else:
            raise Exception(f"Unexpected response: {response}")

    except Exception as e:
        print(f"Error calling {method}: {e}")
        raise


def simulate_transaction(
    tx: Dict[str, Any], block_identifier: str = "latest"
) -> Dict[str, Any]:
    """
    Simulate a single transaction using eth_call and eth_estimateGas

    Returns a SimulationResult in eth_simulateV1 format
    """
    try:
        # Get gas estimate
        gas_estimate = call_backend("eth_estimateGas", [tx, block_identifier])
        gas_used = (
            int(gas_estimate, 16) if isinstance(gas_estimate, str) else gas_estimate
        )

        # Execute eth_call to get output
        output = call_backend("eth_call", [tx, block_identifier])

        # For deposit transactions, we need special handling
        tx.get("depositTxVersion") is not None

        # Create simulation result
        result = {
            "gasUsed": int_to_hex(gas_used),
            "logs": [],  # Would need to use trace_transaction or similar
            "output": output if output else "0x",
            "returnData": output if output else "0x",
            "status": "0x1",  # Success
        }

        # Add additional fields if needed
        result["accountAccesses"] = []
        result["logsBloom"] = "0x" + "00" * 256

        return result

    except Exception as e:
        print(f"Error simulating transaction: {e}")
        # Return failed result
        return {
            "gasUsed": "0x0",
            "logs": [],
            "output": "0x",
            "returnData": "0x",
            "status": "0x0",  # Failure
            "error": str(e),
        }


@app.route("/", methods=["POST"])
def handle_rpc():
    """Handle RPC requests"""
    try:
        data = request.get_json()

        if not data or "method" not in data:
            return (
                jsonify(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32600, "message": "Invalid Request"},
                        "id": data.get("id") if data else None,
                    }
                ),
                400,
            )

        method = data["method"]
        params = data.get("params", [])
        req_id = data.get("id")

        # Handle eth_simulateV1
        if method == "eth_simulateV1":
            return handle_eth_simulate_v1(params, req_id)

        # Handle other methods by proxying
        elif method.startswith("eth_"):
            return proxy_to_backend(method, params, req_id)

        # Unknown method
        else:
            return (
                jsonify(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": "Method not found"},
                        "id": req_id,
                    }
                ),
                404,
            )

    except Exception as e:
        print(f"Error handling request: {e}")
        return (
            jsonify(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                    "id": request.get_json().get("id") if request.is_json else None,
                }
            ),
            500,
        )


def handle_eth_simulate_v1(params: List[Any], req_id: Any) -> Any:
    """Handle eth_simulateV1 RPC method"""
    try:
        # Extract parameters
        transactions = params[0] if len(params) > 0 else []
        block_identifier = params[1] if len(params) > 1 else "latest"

        if not isinstance(transactions, list):
            return (
                jsonify(
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32602,
                            "message": "Invalid parameters: transactions must be array",
                        },
                        "id": req_id,
                    }
                ),
                400,
            )

        # Simulate each transaction
        results = []
        for tx in transactions:
            result = simulate_transaction(tx, block_identifier)
            results.append(result)

        # Return results in eth_simulateV1 format
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": results})

    except Exception as e:
        print(f"Error in eth_simulateV1: {e}")
        return (
            jsonify(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                    "id": req_id,
                }
            ),
            500,
        )


def proxy_to_backend(method: str, params: List[Any], req_id: Any) -> Any:
    """Proxy other RPC methods to backend"""
    try:
        result = call_backend(method, params)
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": result})
    except Exception as e:
        return (
            jsonify(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": str(e)},
                    "id": req_id,
                }
            ),
            500,
        )


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    try:
        # Check if backend is available
        block = call_backend("eth_blockNumber", [])
        return (
            jsonify(
                {"status": "healthy", "backend": "connected", "latest_block": block}
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {"status": "unhealthy", "backend": "disconnected", "error": str(e)}
            ),
            503,
        )


@app.route("/ready", methods=["GET"])
def ready():
    """Readiness check endpoint"""
    return jsonify({"ready": True}), 200


if __name__ == "__main__":
    print("Starting eth_simulateV1 Proxy Service...")
    print(f"Backend: {DEFAULT_BACKEND}")
    print("Listening on port 8545")

    app.run(host="0.0.0.0", port=8545, debug=False)
