# Tutorial 01: Quickstart Clone and CDC Sandbox

In this tutorial, you run an isolated Docker Compose migration lab with `pgcopydb` using the built-in `unit` and `pagila` suites.

## Prerequisites

- Docker and Docker Compose (`docker compose version`)
- GNU Make (`make --version`)
- A local clone of `jmrenouard/pgcopydb` on a Docker-capable Linux or WSL host
- No external production PostgreSQL URI configured (all traffic stays inside isolated Compose networks)

## Step 1 — Verify Helper Scripts and Local Environment

Inspect the local script syntax and container CLI before building test images:

```bash
bash -n ./build_rhel8.sh ./run_migration.sh ./tests/unit/script/9-version-parsing.sh
./build_rhel8.sh --help
./run_migration.sh --help
```

Expected output:

```text
Usage: build_rhel8.sh [--help]
Build pgcopydb inside Rocky Linux 8 using Dockerfile.rhel8 and extract ./pgcopydb-rhel8.
Usage: run_migration.sh [--help]
Run pgcopydb-rhel8 clone using PGCOPYDB_SOURCE_PGURI and PGCOPYDB_TARGET_PGURI (from environment or .env).
Optional variables: TABLE_JOBS (default 8), INDEX_JOBS (default 8).
```

## Step 2 — Run the Isolated Unit Test Container

Build the sandbox PostgreSQL images (`PGVERSION=16` by default) and run the `unit` Compose suite:

```bash
PGVERSION=16 make tests/unit
```

Expected terminal summary (`tests/unit/copydb.sh` finishes with exit code `0`):

```text
pgcopydb ping
...
Version parsing test suite: PASSED
```

## Step 3 — Run the Full `pagila` End-to-End Clone Lab

Run the canonical `pagila` regression suite (schema, COPY data, indexes, constraints, sequences, and blobs) inside its throwaway Compose project:

```bash
PGVERSION=16 make tests/pagila
```

Expected result: Docker Compose starts `source` and `target` containers, executes `pgcopydb clone`, verifies row counts and sequences, and tears down the containers cleanly.

## Step 4 — Clean Up Cached Images (Optional)

When you finish testing or switch `PGVERSION`, remove cached `pgcopydb` and `pagila` images:

```bash
make clean-images
```

## Next Steps

- Build the RHEL8 binary and verify version parsing in [Tutorial 02](02-rhel8-build-and-version-lab.md).
- Follow operational runbooks in [How-To Guides](../02-how-to-guides/index.md).
- Inspect all CLI options and variables in [CLI Commands and Env Vars](../03-reference/01-cli-commands-and-env-vars.md).
- Understand streaming architecture in [Streaming COPY and CDC Architecture](../04-explanation/01-streaming-copy-and-cdc-architecture.md).
