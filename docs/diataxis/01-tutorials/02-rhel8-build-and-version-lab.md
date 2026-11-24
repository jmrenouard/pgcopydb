# Tutorial 02: RHEL8 Build and 3-Digit Version Lab

In this tutorial, you verify the Rocky Linux 8 build pipeline (`Dockerfile.rhel8`) and inspect the 3-digit PostgreSQL version parser fix (`16.14.0`, `18.3.10`).

## Prerequisites

- Docker Engine running on x86_64 Linux or WSL
- `bash` and `pg_config` / `gcc` (optional, for local C syntax verification)
- Outbound HTTPS access inside Docker to pull `rockylinux:8`, EPEL, and PGDG RPMs

## Step 1 — Inspect the Version Parsing Regression Test

Review the fork's regression test cases in [tests/unit/9-version-parsing.c](../../../tests/unit/9-version-parsing.c) and [tests/unit/expected/9-version-parsing.out](../../../tests/unit/expected/9-version-parsing.out):

```bash
bash ./tests/unit/script/9-version-parsing.sh
```

Expected output:

```text
=== Version Parsing Test Suite ===
Testing version: 16.3
Testing version: 18.1
Testing version: 16.14.0
Testing version: 18.3.10
Version parsing test suite: PASSED
```

Verify that [tests/unit/9-version-parsing.c](../../../tests/unit/9-version-parsing.c) passes C preprocessing and syntax checks when PostgreSQL headers are installed locally:

```bash
gcc -fsyntax-only -std=c99 \
  -Isrc/bin/pgcopydb -Isrc/bin/lib/log/src -Isrc/bin/lib/libs \
  -Isrc/bin/lib/pg -Isrc/bin/lib/parson -Isrc/bin/lib/subcommands.c \
  -I"$(pg_config --includedir)" tests/unit/9-version-parsing.c
```

## Step 2 — Run the Automated RHEL8 Build Script

Execute `./build_rhel8.sh` to build the `pgcopydb:rhel8` Docker image and extract `./pgcopydb-rhel8`:

```bash
./build_rhel8.sh
```

Expected final verification lines:

```text
[SUCCESS] Red Hat 8 binary generated successfully:
...
Compiled binary version:
pgcopydb version 0.18
```

## Step 3 — Verify Script Dry-Run Guard Without Credentials

Run `./run_migration.sh` in a temporary directory without `.env` or environment variables to confirm fail-safe guard behavior:

```bash
env -i PATH="$PATH" ./run_migration.sh || true
```

Expected error message:

```text
[ERROR] PGCOPYDB_SOURCE_PGURI and PGCOPYDB_TARGET_PGURI must be set in .env or the environment.
```

## Next Steps

- Deploy the extracted binary cleanly with [Build and Deploy RHEL8 Binary](../02-how-to-guides/01-build-and-deploy-rhel8-binary.md).
- Run production migrations with [Run Offline and CDC Migrations](../02-how-to-guides/02-run-offline-and-cdc-migrations.md).
- Inspect exact script parameters in [RHEL8 Scripts and Version Parsing](../03-reference/02-rhel8-scripts-and-version-parsing.md).
- Read fork design and credential notes in [RHEL8 Packaging and Credential Posture](../04-explanation/02-rhel8-fork-packaging-and-credential-posture.md).
