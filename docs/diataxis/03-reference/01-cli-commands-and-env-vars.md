# CLI Commands and Environment Variables

## Top-Level Subcommands

| Command | Purpose | Key Subcommands / Options |
| :--- | :--- | :--- |
| `pgcopydb clone` | Full database copy (optional online CDC) | `--source`, `--target`, `--table-jobs`, `--index-jobs`, `--follow`, `--resume`, `--all-databases` |
| `pgcopydb fork` | Alias for `clone` | Inherits `clone` options |
| `pgcopydb follow` | Logical decoding replication client (`pgoutput`, `test_decoding`, `wal2json`) | `--plugin`, `--slot-name`, `--origin`, `--endpos` |
| `pgcopydb snapshot` | Export and hold a consistent PostgreSQL transaction snapshot | `--source`, `--dir` |
| `pgcopydb compare` | Verify source and target equivalence | `schema`, `data` |
| `pgcopydb copy` | Execute individual copy phases | `db`, `roles`, `extensions`, `schema`, `data`, `table-data`, `blobs`, `sequences`, `indexes`, `constraints` |
| `pgcopydb dump` | Dump source schema or roles to work directory | `schema`, `roles` |
| `pgcopydb restore` | Restore dumped schema or roles to target | `schema`, `pre-data`, `post-data`, `roles`, `parse-list` |
| `pgcopydb list` | Inspect source objects or SQLite progress | `databases`, `extensions`, `collations`, `tables`, `table-parts`, `sequences`, `indexes`, `depends`, `schema`, `progress` |
| `pgcopydb stream` | Low-level CDC pipeline and sentinel control | `setup`, `cleanup`, `prune`, `prefetch`, `catchup`, `replay`, `sentinel`, `receive`, `apply` |
| `pgcopydb ping` | Verify source and target PostgreSQL connectivity | `--source`, `--target` |
| `pgcopydb version` | Print `pgcopydb` and PostgreSQL client build version | `--json` |
| `pgcopydb help` | Print command tree or subcommand help | `[command]` |

## Environment Variables and Work Directory Paths

| Variable / Path | Default | Scope | Description |
| :--- | :--- | :--- | :--- |
| `PGCOPYDB_SOURCE_PGURI` | unset | Source client | Libpq connection URI for the source PostgreSQL instance |
| `PGCOPYDB_TARGET_PGURI` | unset | Target client | Libpq connection URI for the target PostgreSQL instance |
| `PGCOPYDB_TABLE_JOBS` | CLI default | `clone` / `copy` | Parallel COPY worker count (`TABLE_JOBS` in `run_migration.sh` defaults to `8`) |
| `PGCOPYDB_INDEX_JOBS` | CLI default | `clone` / `copy` | Concurrent `CREATE INDEX` worker count (`INDEX_JOBS` in `run_migration.sh` defaults to `8`) |
| `PGCOPYDB_SPLIT_TABLES_LARGER_THAN` | unset | `clone` / `copy` | Threshold size for same-table CTID/range partitioning |
| `PG_CONFIG` | lookup in `PATH` | Runtime & build | Locates matching `pg_dump`, `pg_restore`, and C dev headers |
| `TMPDIR` | `/tmp` (`/var/run/pgcopydb` in tests) | Work directory | Root directory storing `schema/source.db`, `schema/filter.db`, `schema/target.db`, `pgcopydb.pid` |
| `XDG_DATA_HOME` | `~/.local/share` | CDC state | Root directory storing SQLite WAL stores (`*-output.db`, `*-replay.db`) |
| `PGVERSION` | `16` | `Makefile` Docker builds | Target PostgreSQL major version (`16`, `17`, `18`) for test containers |
