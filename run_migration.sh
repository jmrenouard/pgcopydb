#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

if [ -f "${ENV_FILE}" ]; then
  echo "[INFO] Chargement du fichier de configuration .env"
  set -a
  source "${ENV_FILE}"
  set +a
fi

if [ -z "${PGCOPYDB_SOURCE_PGURI:-}" ] || [ -z "${PGCOPYDB_TARGET_PGURI:-}" ]; then
  echo "[ERREUR] Les variables PGCOPYDB_SOURCE_PGURI et PGCOPYDB_TARGET_PGURI doivent être définies dans le fichier .env ou l'environnement."
  echo "Veuillez éditer le fichier .env et renseigner les accès réels :"
  echo '  PGCOPYDB_SOURCE_PGURI="postgres://enterprisedb:pass@source-host:5444/mydb"'
  echo '  PGCOPYDB_TARGET_PGURI="postgres://enterprisedb:pass@target-host:5444/mydb"'
  exit 1
fi

LOG_FILE="${SCRIPT_DIR}/migration_$(date +%Y%m%d_%H%M%S).log"

echo "[INFO] Lancement de la migration pgcopydb pour EnterpriseDB..."
echo "[INFO] Source : $(echo "${PGCOPYDB_SOURCE_PGURI}" | sed -E 's/:[^@]+@/:***@/')"
echo "[INFO] Cible  : $(echo "${PGCOPYDB_TARGET_PGURI}" | sed -E 's/:[^@]+@/:***@/')"
echo "[INFO] Fichier de journalisation : ${LOG_FILE}"

"${SCRIPT_DIR}/pgcopydb-rhel8" clone \
  --source "${PGCOPYDB_SOURCE_PGURI}" \
  --target "${PGCOPYDB_TARGET_PGURI}" \
  --table-jobs "${TABLE_JOBS:-8}" \
  --index-jobs "${INDEX_JOBS:-8}" 2>&1 | tee "${LOG_FILE}"

echo "[SUCCÈS] Migration EnterpriseDB terminée avec succès !"
