#!/bin/bash

set -e

echo "=========================================="
echo "Building op-reth with eth_simulateV1"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    log_error "Docker is not running"
    exit 1
fi

# Check for Rust toolchain
if ! command -v rustc &> /dev/null; then
    log_warn "Rust not found locally, will use Docker build"
else
    RUST_VERSION=$(rustc --version)
    log_info "Rust version: $RUST_VERSION"
fi

# Set build arguments
RETH_VERSION=${RETH_VERSION:-"v1.0.0-rc.4"}
IMAGE_NAME="ghcr.io/unitsnetwork/op-reth:simulate-v1"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=${VCS_REF:-"local"}

log_info "Building Reth version: $RETH_VERSION"
log_info "Target image: $IMAGE_NAME"
log_info ""

# Check if patch exists
if [ ! -f "$PROJECT_ROOT/patches/eth_simulateV1.patch" ]; then
    log_warn "eth_simulateV1.patch not found"
    log_warn "This means standard Reth will be built (without eth_simulateV1 support)"
    log_warn ""
    log_warn "To add eth_simulateV1 support:"
    log_warn "1. Create patches/eth_simulateV1.patch with the implementation"
    log_warn "2. See docs/ETH_SIMULATE_V1_IMPLEMENTATION_NOTES.md for details"
    log_warn ""

    read -p "Continue building standard Reth? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Build cancelled"
        exit 0
    fi
else
    log_info "Found eth_simulateV1.patch, will apply during build"
fi

# Build image
log_info "Building Docker image..."
log_info ""

DOCKER_BUILDKIT=1 docker build \
    --build-arg RETH_VERSION="$RETH_VERSION" \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg VCS_REF="$VCS_REF" \
    -t "$IMAGE_NAME" \
    -f "$PROJECT_ROOT/docker/Dockerfile.op-reth-simulate" \
    "$PROJECT_ROOT"

if [ $? -eq 0 ]; then
    log_info ""
    log_info "=========================================="
    log_info "Build completed successfully!"
    log_info "=========================================="
    log_info ""
    log_info "Image: $IMAGE_NAME"
    log_info "Reth version: $RETH_VERSION"
    log_info ""
    log_info "To use in Docker Compose:"
    log_info "  export OP_RETH_IMAGE=$IMAGE_NAME"
    log_info "  docker-compose up -d ec-2"
    log_info ""
    log_info "To push to registry:"
    log_info "  docker push $IMAGE_NAME"
    log_info ""

    # Test the image
    log_info "Testing the image..."
    docker run --rm "$IMAGE_NAME" reth --version || true
else
    log_error "Build failed"
    exit 1
fi
