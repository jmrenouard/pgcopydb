# RHEL8 Packaging and Credential Posture

The `jmrenouard/pgcopydb` fork extends upstream `pgcopydb` for EnterpriseDB/PostgreSQL 16–18 migrations hosted on Red Hat Enterprise Linux 8 and Rocky Linux 8.

## Why 3-Digit Dotted Version Parsing Was Added

Upstream `parse_dotted_version_string()` rejected any PostgreSQL version string containing a second period (`Failed to parse Postgres version number`), assuming `MAJOR.MINOR` pairs such as `16.3`. Minor point releases and EnterpriseDB/community toolchains reporting three segments (`16.13.0`, `16.14.0`, `17.7.2`, `18.3.10`) failed version discovery during `clone`. Breaking out of the loop on the second dot preserves existing `major * 100 + minor` integers (`1614`, `1803`) without changing catalog compatibility.

## Rocky Linux 8 Build and Runtime Dependencies

Compiling `pgcopydb` inside [Dockerfile.rhel8](../../../Dockerfile.rhel8) isolates PGDG (`postgresql16-devel`) and Boehm GC (`gc-devel`) build headers in a container, extracting a portable `pgcopydb-rhel8` binary to the host. Three operational trade-offs apply:

- **Dynamic library linkage:** `pgcopydb-rhel8` dynamically links `libpq.so.5` and `libgc.so.1`, so target RHEL8 hosts must install `gc` and `postgresql16-libs` even when running the prebuilt binary.
- **Bootstrap GPG bypass:** `Dockerfile.rhel8` passes `dnf install -y --nogpgcheck` to install `pgdg-redhat-repo-latest.noarch.rpm` on an unpinned `rockylinux:8` tag, trading supply-chain strictness for one-step image assembly.
- **Credential visibility:** [run_migration.sh](../../../run_migration.sh) masks passwords in log output with `sed`, yet passes `--source` and `--target` arguments to `pgcopydb-rhel8`. On shared hosts, running `pgcopydb` with exported `PGCOPYDB_SOURCE_PGURI` and `PGCOPYDB_TARGET_PGURI` variables prevents URI passwords from appearing in `ps` output.

## Fork Documentation Layout and Tag Safety

Because Sphinx builds `docs/index.rst` and `.github/workflows/run-tests.yml` runs `ci/check-docs.mk` (`make update-docs`) against `docs/include/*.rst`, fork Diátaxis guides live under `docs/diataxis/` and are excluded in `docs/conf.py`. Likewise, because `docker-publish.yml` and `homebrew-bump.yml` match `tags: ['v*.*']`, fork milestone releases use annotated `release-*` tags (`release-1.0.0`) so upstream container and Homebrew jobs are not triggered unintentionally.

## Related Documentation

- Script specifications and C test matrix: [RHEL8 Scripts and Version Parsing](../03-reference/02-rhel8-scripts-and-version-parsing.md)
- Operational deployment guide: [Build and Deploy the RHEL8 Binary](../02-how-to-guides/01-build-and-deploy-rhel8-binary.md)
