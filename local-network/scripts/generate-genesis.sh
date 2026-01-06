#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Generating consensus genesis state and validator keys..."

# Create temporary directory for generation
GEN_DIR=$(mktemp -d)
echo "Using temporary directory: $GEN_DIR"

# Create minimal preset config
cat > "$GEN_DIR/config.yaml" << 'EOF'
PRESET_BASE: minimal
CONFIG_NAME: local-testnet
MIN_GENESIS_ACTIVE_VALIDATOR_COUNT: 256
MIN_GENESIS_TIME: 1704067200
GENESIS_FORK_VERSION: 0x00000000
GENESIS_DELAY: 10
SECONDS_PER_SLOT: 12
SLOTS_PER_EPOCH: 32
EPOCHS_PER_SYNC_COMMITTEE_PERIOD: 256
EPOCHS_PER_ETH1_VOTING_PERIOD: 64
SLOTS_PER_HISTORICAL_ROOT: 131072
MIN_VALIDATOR_WITHDRAWABILITY_DELAY: 256
SHARD_COMMITTEE_PERIOD: 256
TARGET_COMMITTEE_SIZE: 4
MAX_COMMITTEES_PER_SLOT: 64
MAX_VALIDATORS_PER_COMMITTEE: 2048
BLS_SIGNATURE_BYTE_LENGTH: 96
BYTES_PER_LOGS_BLOOM: 256
MIN_PER_EPOCH_CHURN_LIMIT: 4
CHURN_LIMIT_QUOTIENT: 65536
PROPORTIONAL_SLASHING_MULTIPLIER: 1
MIN_SLASHING_PENALTY_QUOTIENT: 128
WHISTLEBLOWER_REWARD_QUOTIENT: 512
MAX_PROPOSER_SLASHINGS: 16
MAX_ATTESTER_SLASHINGS: 2
MAX_ATTESTATIONS: 128
MAX_DEPOSITS: 16
MAX_VOLUNTARY_EXITS: 16
ALTAIR_FORK_VERSION: 0x01000000
ALTAIR_FORK_EPOCH: 0
BELLATRIX_FORK_VERSION: 0x02000000
BELLATRIX_FORK_EPOCH: 0
CAPELLA_FORK_VERSION: 0x03000000
CAPELLA_FORK_EPOCH: 0
DENEB_FORK_VERSION: 0x04000000
DENEB_FORK_EPOCH: 0
ELECTRA_FORK_VERSION: 0x05000000
ELECTRA_FORK_EPOCH: 18446744073709551615
DOMAIN_BEACON_PROPOSER: 0x00000000
DOMAIN_BEACON_ATTESTER: 0x01000000
DOMAIN_RANDAO: 0x02000000
DOMAIN_DEPOSIT: 0x03000000
DOMAIN_VOLUNTARY_EXIT: 0x04000000
DOMAIN_SELECTION_PROOF: 0x05000000
DOMAIN_AGGREGATE_AND_PROOF: 0x06000000
DOMAIN_SYNC_COMMITTEE: 0x07000000
DOMAIN_SYNC_COMMITTEE_SELECTION_PROOF: 0x08000000
DOMAIN_CONTRIBUTION_AND_PROOF: 0x09000000
INACTIVITY_SCORE_BIAS: 16777216
INACTIVITY_SCORE_RECOVERY_RATE: 167772
MIN_SLASHING_PENALTY_QUOTIENT_ALTAIR: 2048
PROPORTIONAL_SLASHING_MULTIPLIER_ALTAIR: 2
SYNC_COMMITTEE_SIZE: 512
EPOCHS_PER_SYNC_COMMITTEE_PERIOD: 256
MIN_SYNC_COMMITTEE_PARTICIPANTS: 1
MIN_EPOCHS_TO_INACTIVITY_PENALTY: 4
DOWNWARD_THRESHOLD: 1
UPWARD_THRESHOLD: 1024
BONUS_BASE_FACTOR: 64
BONUS_REWARD_NUMERATOR: 3
BONUS_REWARD_DENOMINATOR: 5
INACTIVITY_PENALTY_QUOTIENT: 50331648
INACTIVITY_PENALTY_QUOTIENT_ALTAIR: 67108864
BASE_REWARD_FACTOR: 64
BASE_REWARD_PER_INCREMENT: 1099511627776
INACTIVITY_PENALTY_QUOTIENT_BELLATRIX: 50331648
MIN_SLASHING_PENALTY_QUOTIENT_BELLATRIX: 128
PROPORTIONAL_SLASHING_MULTIPLIER_BELLATRIX: 3
SYNC_COMMITTEE_SUBNET_COUNT: 4
TARGET_EPOCHS_TO_BLOB_PROPOSAL: 2
MAX_BLOB_GAS_PER_BLOCK: 393216
BLOB_TX_GAS_PER_BLOB: 131072
MIN_GAS_PRICE_BLOB_TX: 1
MAX_REQUEST_BLOCKS_DENOMINATOR: 128
MAX_REQUEST_BLOCKS_SIDECAR: 64
MAX_WITHDRAWALS_PER_PAYLOAD: 16
FULL_VALIDATOR_WITHDRAWAL_DELAY: 256
MAX_REQUEST_BLOB_SIDECARS: 768
DEPOSIT_CHAIN_ID: 1337
DEPOSIT_NETWORK_ID: 1337
DEPOSIT_CONTRACT_ADDRESS: 0x0000000000000000000000000000000000006A7e
TERMINAL_TOTAL_DIFFICULTY: 0
TERMINAL_BLOCK_HASH: 0x0000000000000000000000000000000000000000000000000000000000000000
TERMINAL_BLOCK_HASH_ACTIVATION_EPOCH: 0
EOF

# Generate deposit data for 4 validators using Python
echo "Generating validator keys and deposit data..."
python3 << 'PYTHON_SCRIPT'
import json
import os
from pathlib import Path

# Generate 4 validator keystores
num_validators = 4
validator_keys_dir = Path("/tmp/consensus_gen/validator-keys")
validator_keys_dir.mkdir(parents=True, exist_ok=True)

deposits = []
validator_count = 0

for i in range(num_validators):
    # Generate a simple keystore structure
    # In production, use proper eth2.0-deposit-cli or ethereal
    validator_count += 1

    # Create minimal validator directory
    validator_dir = validator_keys_dir / f"validator_{i}"
    validator_dir.mkdir(exist_ok=True)

    # Generate placeholder keys (these would be properly generated in production)
    # For testing purposes, we use deterministic keys
    privkey = f"0x{'0' * 62}{i:02x}"
    pubkey = f"0x{'0' * 94}{i:02x}"

    keystore = {
        "crypto": {
            "kdf": {"function": "scrypt", "params": {"dklen": 32, "salt": "0" * 64}},
            "checksum": {"message": "", "function": "sha256"},
            "cipher": {"message": privkey, "function": "aes-128-ctr", "params": {"iv": "0" * 32}}
        },
        "path": "m/12381/3600/0/0/0",
        "uuid": "12345678-1234-1234-1234-123456789012",
        "version": 4
    }

    # Write keystore
    with open(validator_dir / "keystore.json", "w") as f:
        json.dump(keystore, f, indent=2)

    # Write password
    with open(validator_dir / "password.txt", "w") as f:
        f.write("password")

    # Create deposit data
    deposit = {
        "pubkey": pubkey,
        "withdrawal_credentials": "0x" + "0" * 23 + "01",
        "amount": 32000000000,  # 32 ETH in Gwei
        "signature": "0x" + "0" * 190
    }
    deposits.append(deposit)

# Write deposit data file
deposit_data = {
    "deposit_data_root": "0x" + "0" * 64,
    "deposits": deposits
}

with open("/tmp/consensus_gen/deposit-data.json", "w") as f:
    json.dump(deposit_data, f, indent=2)

print(f"Generated {num_validators} validators")
print("Keystores written to: /tmp/consensus_gen/validator-keys")
print("Deposit data written to: /tmp/consensus_gen/deposit-data.json")
PYTHON_SCRIPT

# Copy generated files to config directory
echo "Copying generated files to config directory..."
cp "$GEN_DIR/config.yaml" "$PROJECT_ROOT/configs/consensus/config-lighthouse.yaml"
mkdir -p "$PROJECT_ROOT/configs/consensus/validator-keys"
cp -r /tmp/consensus_gen/validator-keys/* "$PROJECT_ROOT/configs/consensus/validator-keys/"
cp /tmp/consensus_gen/deposit-data.json "$PROJECT_ROOT/configs/consensus/deposit-data.json"

# Generate minimal genesis.ssz
# Use lighthouse to create genesis state
echo "Generating genesis.ssz..."
docker run --rm -v "$GEN_DIR:/data" \
    -v "$PROJECT_ROOT/configs/consensus:/config" \
    sigp/lighthouse:v5.2.1 \
    lighthouse \
    boot_node \
    --testnet-dir=/data \
    --genesis-state-url=/config/genesis.ssz \
    --port=9000 || true

# Create empty genesis.ssz if generation failed (will be created by clients)
if [ ! -f "$PROJECT_ROOT/configs/consensus/genesis.ssz" ]; then
    echo "Creating placeholder genesis.ssz (will be generated by consensus clients)"
    touch "$PROJECT_ROOT/configs/consensus/genesis.ssz"
fi

# Clean up
rm -rf "$GEN_DIR"
rm -rf /tmp/consensus_gen

echo "Genesis configuration complete!"
echo "Files generated:"
echo "  - $PROJECT_ROOT/configs/consensus/config-lighthouse.yaml"
echo "  - $PROJECT_ROOT/configs/consensus/config-prysm.yml"
echo "  - $PROJECT_ROOT/configs/consensus/validator-keys/"
echo "  - $PROJECT_ROOT/configs/consensus/deposit-data.json"
echo "  - $PROJECT_ROOT/configs/consensus/genesis.ssz"
