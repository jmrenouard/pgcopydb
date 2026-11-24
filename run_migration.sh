#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    echo "Usage: $(basename "$0") [--help]"
    echo "Run pgcopydb-rhel8 clone using PGCOPYDB_SOURCE_PGURI and PGCOPYDB_TARGET_PGURI (from environment or .env)."
    echo "Optional variables: TABLE_JOBS (default 8), INDEX_JOBS (default 8)."
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

if [ -f "${ENV_FILE}" ]; then
  echo "[INFO] Loading configuration file .env"
  set -a
  source "${ENV_FILE}"
  set +a
fi

if [ -z "${PGCOPYDB_SOURCE_PGURI:-}" ] || [ -z "${PGCOPYDB_TARGET_PGURI:-}" ]; then
  echo "[ERROR] PGCOPYDB_SOURCE_PGURI and PGCOPYDB_TARGET_PGURI must be set in .env or the environment."
  echo "Edit .env and configure your connection URIs:"
  echo '  PGCOPYDB_SOURCE_PGURI="postgres://enterprisedb:pass@source-host:5444/mydb"'
  echo '  PGCOPYDB_TARGET_PGURI="postgres://enterprisedb:pass@target-host:5444/mydb"'
  exit 1
fi

LOG_FILE="${SCRIPT_DIR}/migration_$(date +%Y%m%d_%H%M%S).log"

echo "[INFO] Starting pgcopydb migration for EnterpriseDB..."
echo "[INFO] Source : $(echo "${PGCOPYDB_SOURCE_PGURI}" | sed -E 's/:[^@]+@/:***@/')"
echo "[INFO] Target : $(echo "${PGCOPYDB_TARGET_PGURI}" | sed -E 's/:[^@]+@/:***@/')"
echo "[INFO] Log file: ${LOG_FILE}"

"${SCRIPT_DIR}/pgcopydb-rhel8" clone \
  --source "${PGCOPYDB_SOURCE_PGURI}" \
  --target "${PGCOPYDB_TARGET_PGURI}" \
  --table-jobs "${TABLE_JOBS:-8}" \
  --index-jobs "${INDEX_JOBS:-8}" 2>&1 | tee "${LOG_FILE}"

echo "[SUCCESS] EnterpriseDB migration completed successfully."
