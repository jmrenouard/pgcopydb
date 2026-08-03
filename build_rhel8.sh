#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IMAGE_NAME="pgcopydb:rhel8"
OUTPUT_BINARY="${SCRIPT_DIR}/pgcopydb-rhel8"
DOCKERFILE="${SCRIPT_DIR}/Dockerfile.rhel8"

echo "=========================================================="
echo " Compilation de pgcopydb pour Red Hat 8 / Rocky Linux 8 "
echo "=========================================================="

if ! command -v docker &> /dev/null; then
    echo "[ERREUR] Docker n'est pas installé ou n'est pas accessible."
    exit 1
fi

if [ ! -f "${DOCKERFILE}" ]; then
    echo "[ERREUR] Le fichier ${DOCKERFILE} est introuvable."
    exit 1
fi

echo "[1/3] Construction de l'image conteneur Red Hat 8 et compilation..."
docker build --progress=plain -f "${DOCKERFILE}" -t "${IMAGE_NAME}" "${SCRIPT_DIR}"

echo "[2/3] Extraction du binaire compilé 'pgcopydb-rhel8'..."
docker run --rm -v "${SCRIPT_DIR}:/mnt" "${IMAGE_NAME}" bash -c "cp /pgcopydb/src/bin/pgcopydb/pgcopydb /mnt/pgcopydb-rhel8 && chmod 755 /mnt/pgcopydb-rhel8"

echo "[3/3] Vérification du binaire généré..."
if [ -f "${OUTPUT_BINARY}" ]; then
    echo "[SUCCÈS] Binaire Red Hat 8 généré avec succès :"
    ls -lh "${OUTPUT_BINARY}"
    echo ""
    echo "Information sur le binaire :"
    file "${OUTPUT_BINARY}"
    echo ""
    echo "Version du binaire compilé :"
    docker run --rm "${IMAGE_NAME}" ./src/bin/pgcopydb/pgcopydb --version
    echo "=========================================================="
else
    echo "[ERREUR] Échec de l'extraction du binaire."
    exit 1
fi
