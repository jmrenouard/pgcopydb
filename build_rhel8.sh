#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    echo "Usage: $(basename "$0") [--help]"
    echo "Build pgcopydb inside Rocky Linux 8 using Dockerfile.rhel8 and extract ./pgcopydb-rhel8."
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IMAGE_NAME="pgcopydb:rhel8"
OUTPUT_BINARY="${SCRIPT_DIR}/pgcopydb-rhel8"
DOCKERFILE="${SCRIPT_DIR}/Dockerfile.rhel8"

echo "=========================================================="
echo " Building pgcopydb for Red Hat 8 / Rocky Linux 8 "
echo "=========================================================="

if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed or not accessible."
    exit 1
fi

if [ ! -f "${DOCKERFILE}" ]; then
    echo "[ERROR] File ${DOCKERFILE} was not found."
    exit 1
fi

echo "[1/3] Building Red Hat 8 container image and compiling..."
docker build --progress=plain -f "${DOCKERFILE}" -t "${IMAGE_NAME}" "${SCRIPT_DIR}"

echo "[2/3] Extracting compiled binary 'pgcopydb-rhel8'..."
docker run --rm -v "${SCRIPT_DIR}:/mnt" "${IMAGE_NAME}" bash -c "cp /pgcopydb/src/bin/pgcopydb/pgcopydb /mnt/pgcopydb-rhel8 && chmod 755 /mnt/pgcopydb-rhel8"

echo "[3/3] Verifying generated binary..."
if [ -f "${OUTPUT_BINARY}" ]; then
    echo "[SUCCESS] Red Hat 8 binary generated successfully:"
    ls -lh "${OUTPUT_BINARY}"
    echo ""
    echo "Binary metadata:"
    file "${OUTPUT_BINARY}"
    echo ""
    echo "Compiled binary version:"
    docker run --rm "${IMAGE_NAME}" ./src/bin/pgcopydb/pgcopydb --version
    echo "=========================================================="
else
    echo "[ERROR] Failed to extract compiled binary."
    exit 1
fi
