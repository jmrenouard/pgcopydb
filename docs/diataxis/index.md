# pgcopydb Documentation

This Diátaxis portal covers `pgcopydb` CLI workflows and the `jmrenouard/pgcopydb` RHEL8 fork tooling.
Upstream Sphinx reference pages stay in [docs/index.rst](../index.rst).

## Four Quadrants

| Quadrant | Purpose | Entry Point |
| :--- | :--- | :--- |
| **Tutorials** | Guided hands-on labs in Docker sandboxes | [01-tutorials/index.md](01-tutorials/index.md) |
| **How-To Guides** | Goal-oriented operational procedures (ASD-STE100) | [02-how-to-guides/index.md](02-how-to-guides/index.md) |
| **Reference** | CLI commands, environment variables, RHEL8 scripts, version parsing | [03-reference/index.md](03-reference/index.md) |
| **Explanation** | Architecture, CDC SQLite stores, and fork security posture | [04-explanation/index.md](04-explanation/index.md) |

## Quick Links

- Project entry overview: [README.md](../../README.md)
- Contributor architecture guide: [AGENT.md](../../AGENT.md)
- RHEL8 container recipe: [Dockerfile.rhel8](../../Dockerfile.rhel8)
- RHEL8 build script: [build_rhel8.sh](../../build_rhel8.sh)
- RHEL8 migration wrapper: [run_migration.sh](../../run_migration.sh)
