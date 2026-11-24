# RHEL8 Scripts and Version Parsing

## Fork RHEL8 Artifacts

| Artifact | Base / Language | Dependencies | Behavior / Notes |
| :--- | :--- | :--- | :--- |
| [Dockerfile.rhel8](../../../Dockerfile.rhel8) | `rockylinux:8` Docker | `epel-release`, `pgdg-redhat-repo`, `postgresql16-devel`, `gc-devel`, `lz4-devel`, `openssl-devel` | Installs dependencies with `--nogpgcheck`, compiles via `make clean && make -j$(nproc)` |
| [build_rhel8.sh](../../../build_rhel8.sh) | Bash (`set -euo pipefail`) | `docker`, `Dockerfile.rhel8`, `file` | Builds `pgcopydb:rhel8`, extracts `/pgcopydb/src/bin/pgcopydb/pgcopydb` to `./pgcopydb-rhel8` (`0755`), prints version (`--help` supported) |
| [run_migration.sh](../../../run_migration.sh) | Bash (`set -euo pipefail`) | `./pgcopydb-rhel8`, optional `.env` | Sources `.env`, validates URIs, masks passwords in stdout/logs via `sed`, executes `clone --source ... --target ... --table-jobs ${TABLE_JOBS:-8} --index-jobs ${INDEX_JOBS:-8}` (`--help` supported) |
| `pgcopydb-rhel8` | ELF 64-bit x86-64 binary | `libpq.so.5`, `libgc.so.1`, `libssl.so.3`, `libcrypto.so.3`, `libpthread.so.0` | Precompiled RHEL8 binary in repository root (`0755`) |

## 3-Digit Version Parsing (`parsing_utils.c`)

Implemented in `parse_dotted_version_string()` ([src/bin/pgcopydb/parsing_utils.c](../../../src/bin/pgcopydb/parsing_utils.c)) and verified by [tests/unit/9-version-parsing.c](../../../tests/unit/9-version-parsing.c):

| Input String | Parsed `int` Value | Parsing Rule |
| :--- | :--- | :--- |
| `16.3` | `1603` | `major * 100 + minor` |
| `18.1` | `1801` | `major * 100 + minor` |
| `16.14.0` | `1614` | Stops at second `.`, keeping major `16` and minor `14` |
| `18.3.10` | `1803` | Stops at second `.`, keeping major `18` and minor `3` |
| `14` | `1400` | Missing dot defaults minor to `"0"` |

## CI Workflow Tag Triggers

| Workflow File | Event Triggers | Tag Safety Constraint |
| :--- | :--- | :--- |
| `.github/workflows/run-tests.yml` | `push` / `pull_request` on `main`, `workflow_dispatch` | Docker PG16/PG18 matrix, `ci/banned.h.sh`, `citus_indent --check`, Sphinx `docs/` + `ci/check-docs.mk` |
| `.github/workflows/nightly.yml` | `schedule` (`02:00 UTC`), `workflow_dispatch` | Full PG16/17/18 test matrix |
| `.github/workflows/docker-publish.yml` | `push` on `main` and `tags: ['v*.*']`, `workflow_dispatch` | Use `release-*` tags (`release-1.0.0`) instead of `v*.*` on fork releases |
| `.github/workflows/homebrew-bump.yml` | `push` on `tags: ['v*.*']`, `workflow_dispatch` | Use `release-*` tags (`release-1.0.0`) to avoid unintended formula bumps |
