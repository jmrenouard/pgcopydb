# Run Offline and CDC Migrations

This guide tells how to configure database URIs and run offline or Change Data Capture migrations with `pgcopydb`.

**Prerequisites:**

- You must have `pgcopydb` and `pg_dump` / `pg_restore` installed in `PATH`.
- Both the source database and the target database must already exist.
- For CDC migrations, the source PostgreSQL server must have `wal_level = logical`.

WARNING: DO NOT RUN `./run_migration.sh` AGAINST AN ACTIVE PRODUCTION TARGET DATABASE BEFORE YOU VERIFY ITS URI. WRONG TARGET URIS CAN OVERWRITE LIVE DATA OR CAUSE DATA LOSS.

CAUTION: EXPORT CONNECTION URIS IN `.env` OR SHELL VARIABLES INSTEAD OF CLI FLAGS ON MULTI-USER HOSTS. CLI FLAGS ARE VISIBLE IN `ps` PROCESS OUTPUT.

## Procedure

1. Create a local `.env` file with restricted file permissions (`0600`).

   ```bash
   umask 077
   cat > .env <<'EOF'
   PGCOPYDB_SOURCE_PGURI="postgres://migrator@source-host:5432/appdb"
   PGCOPYDB_TARGET_PGURI="postgres://migrator@target-host:5432/appdb"
   EOF
   ```

2. Source the `.env` variables into the shell session.

   ```bash
   set -a && source ./.env && set +a
   ```

3. Test connectivity and permissions on both PostgreSQL servers.

   ```bash
   pgcopydb ping
   ```

4. If you run an offline migration on RHEL 8, execute `./run_migration.sh`.

   ```bash
   ./run_migration.sh
   ```

5. If you run an online CDC migration, start `pgcopydb clone --follow` directly from environment variables.

   ```bash
   pgcopydb clone --follow --table-jobs 8 --index-jobs 4
   ```

NOTE: The `pgcopydb clone --follow` command keeps the replication stream active until you set an end position LSN or stop the process.

## Verification

1. Display the migration progress summary from the SQLite catalog.

   ```bash
   pgcopydb list progress --summary
   ```

2. Query the sentinel table on the source database during CDC migrations.

   ```bash
   psql "${PGCOPYDB_SOURCE_PGURI}" -c "SELECT * FROM pgcopydb.sentinel;"
   ```

3. Inspect the generated log file and confirm zero error lines.

   ```bash
   grep -E "ERROR|FATAL" migration_*.log || echo "No errors found."
   ```

## Rollback

If an incomplete migration stops, remove the work directory and recreate the target schema:

```bash
rm -rf "${TMPDIR:-/tmp}/pgcopydb"
```

If you want to continue from the last SQLite checkpoint instead, add `--resume`:

```bash
pgcopydb clone --resume --table-jobs 8 --index-jobs 4
```

## References

- CLI commands and variables: [CLI Commands and Env Vars](../03-reference/01-cli-commands-and-env-vars.md)
- SQLite design: [Stream COPY and CDC Architecture](../04-explanation/01-streaming-copy-and-cdc-architecture.md)
