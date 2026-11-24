# Build and Deploy the RHEL8 Binary

This guide tells how to build `pgcopydb-rhel8` and install it on a Rocky Linux 8 or RHEL 8 host.

**Prerequisites:**

- You must have Docker installed on the build host.
- You must have SSH access and `sudo` privileges on the target RHEL 8 host.
- You must install the PostgreSQL client runtime and Boehm GC libraries on the target host.

CAUTION: BACK UP ANY EXISTING `pgcopydb-rhel8` BINARY BEFORE YOU REPLACE IT. OVERWRITING AN ACTIVE BINARY CAN BREAK SCHEDULED MIGRATION JOBS.

## Procedure

1. Open the local `pgcopydb` repository root directory.

   ```bash
   cd /path/to/pgcopydb
   ```

2. Check that the build script syntax is valid.

   ```bash
   bash -n ./build_rhel8.sh
   ```

3. Run the RHEL 8 build script to compile and extract `pgcopydb-rhel8`.

   ```bash
   ./build_rhel8.sh
   ```

4. Copy the extracted binary to the target RHEL 8 host.

   ```bash
   scp ./pgcopydb-rhel8 ops@target-rhel8:/tmp/pgcopydb-rhel8
   ```

5. Install the required runtime shared libraries on the target RHEL 8 host.

   ```bash
   sudo dnf install -y gc postgresql16-libs
   ```

6. Move the binary into `/usr/local/bin/pgcopydb` and set executable permissions.

   ```bash
   sudo install -m 0755 /tmp/pgcopydb-rhel8 /usr/local/bin/pgcopydb
   ```

## Verification

1. Print the binary version on the target RHEL 8 host.

   ```bash
   pgcopydb --version
   ```

2. Check that all shared library links resolve with no `not found` lines.

   ```bash
   ldd /usr/local/bin/pgcopydb
   ```

3. Remove the temporary upload file from `/tmp`.

   ```bash
   rm -f /tmp/pgcopydb-rhel8
   ```

## Rollback

If the new binary fails validation, restore the backed-up binary on the target RHEL 8 host:

```bash
sudo mv /usr/local/bin/pgcopydb.bak /usr/local/bin/pgcopydb
pgcopydb --version
```

## References

- Script options and shared library tables: [RHEL8 Scripts and Version Matrix](../03-reference/02-rhel8-scripts-and-version-parsing.md)
- Container trade-offs: [RHEL8 Package and Credential Design](../04-explanation/02-rhel8-fork-packaging-and-credential-posture.md)
