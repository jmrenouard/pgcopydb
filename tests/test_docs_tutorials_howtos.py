"""Automated tests for pgcopydb Diataxis docs, STE rules, Mermaid, and RHEL8 fork artifacts."""

from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIATAXIS_DIR = ROOT / "docs" / "diataxis"
QUADRANTS = ("01-tutorials", "02-how-to-guides", "03-reference", "04-explanation")

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,})(.*)$")
MERMAID_HEAD_RE = re.compile(
    r"^\s*(?:flowchart(?:-elk)?(?:\s+(?:TD|TB|LR|RL|BT))?|graph\s+(?:TD|TB|LR|RL|BT)|"
    r"sequenceDiagram|stateDiagram(?:-v2)?|classDiagram|erDiagram|gantt|pie|gitGraph|"
    r"mindmap|timeline|xychart-beta)\b"
)
BARE_ARROW_RE = re.compile(r"(?:(?<![<!])-->|(?<!<!)<--|(?<![=])==>|─+>|▼|▲)")
BOX_CHAR_RE = re.compile(r"[┌┐┘╔╗╚╝]|\+[-=]{2,}\+")

FORBIDDEN_HOWTO_MODAL_RE = re.compile(
    r"\b(?:should|would|may|might|shall|ought|can't|don't|won't|isn't|aren't|doesn't|didn't)\b",
    re.IGNORECASE,
)
FRENCH_LEAK_RE = re.compile(
    r"(?:\[(?:ERREUR|SUCC[ÈE]S)\]|Chargement du fichier|Veuillez|Lancement de la migration|"
    r"\b(?:échoué|introuvable|terminée|binaire)\b)",
    re.IGNORECASE,
)


def _iter_repo_markdowns() -> list[Path]:
    skip = {".git", "node_modules", ".venv", "__pycache__", "_build"}
    results: list[Path] = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in skip)
        for name in sorted(files):
            if name.lower().endswith(".md"):
                results.append(Path(base) / name)
    return results


def _split_prose_and_code(text: str) -> tuple[list[tuple[str, bool]], list[tuple[str, str, int, str]]]:
    """Return (prose_paragraphs_with_is_note, fenced_blocks[(indent, lang, line, body)])."""
    blocks: list[tuple[str, str, int, str]] = []
    prose: list[tuple[str, bool]] = []
    para_lines: list[str] = []
    in_fence = False
    fchar = ""
    flen = 0
    findent = ""
    flang = ""
    fline = 0
    fbody: list[str] = []

    def flush_para() -> None:
        if para_lines:
            joined = " ".join(para_lines).strip()
            if joined:
                prose.append((joined, joined.upper().startswith("NOTE:")))
            para_lines.clear()

    for idx, line in enumerate(text.splitlines(), start=1):
        if not in_fence:
            m = FENCE_RE.match(line)
            if m and not (m.group(2)[0] == "`" and "`" in m.group(3)):
                flush_para()
                in_fence = True
                findent = m.group(1)
                fchar = m.group(2)[0]
                flen = len(m.group(2))
                flang = m.group(3).strip().split()[0].lower() if m.group(3).strip() else ""
                fline = idx
                fbody = []
                continue
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("|") or re.match(r"^[-*_]{3,}$", stripped):
                flush_para()
                continue
            cleaned = re.sub(r"^(?:>\s*|[-*+]\s+|\d+\.\s+)", "", stripped)
            para_lines.append(cleaned)
        else:
            if re.match(rf"^[ \t]*{re.escape(fchar)}{{{flen},}}[ \t]*$", line):
                blocks.append((findent, flang, fline, "\n".join(fbody)))
                in_fence = False
            else:
                fbody.append(line)
    flush_para()
    return prose, blocks


def _find_mmdc() -> str | None:
    if found := shutil.which("mmdc"):
        return found
    candidate = Path("/home/jmren/node_modules/.bin/mmdc")
    return str(candidate) if candidate.is_file() else None


class TestPgcopydbDocsAndRhel8(unittest.TestCase):
    """Verify Diataxis documentation, STE compliance, Mermaid diagrams, and RHEL8 fork scripts."""

    def test_diataxis_structure_links_and_sphinx_exclusion(self) -> None:
        """Check Sphinx exclusion of docs/diataxis, quadrant trees, genre isolation, and relative links."""
        conf_src = (ROOT / "docs" / "conf.py").read_text(encoding="utf-8")
        tree = ast.parse(conf_src)
        excluded = None
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "exclude_patterns":
                        excluded = ast.literal_eval(node.value)
        self.assertIsInstance(excluded, list)
        self.assertIn("diataxis", excluded)

        self.assertTrue((DIATAXIS_DIR / "index.md").is_file())
        for q in QUADRANTS:
            qdir = DIATAXIS_DIR / q
            self.assertTrue((qdir / "index.md").is_file(), f"Missing {q}/index.md")
            pages = [p for p in sorted(qdir.glob("*.md")) if p.name != "index.md"]
            self.assertGreaterEqual(len(pages), 2, f"Expected >=2 pages in {q}")

        for page in sorted((DIATAXIS_DIR / "01-tutorials").glob("*.md")):
            if page.name == "index.md":
                continue
            txt = page.read_text(encoding="utf-8")
            self.assertIn("## Prerequisites", txt)
            self.assertIn("## Next Steps", txt)

        for page in sorted((DIATAXIS_DIR / "03-reference").glob("*.md")):
            txt = page.read_text(encoding="utf-8")
            for banned in ("In this tutorial", "Let's ", "Step 1"):
                self.assertNotIn(banned, txt, f"{page.name} mixes tutorial phrasing: {banned}")

        for page in sorted((DIATAXIS_DIR / "04-explanation").glob("*.md")):
            txt = page.read_text(encoding="utf-8")
            for banned in ("## Step 1", "## Rollback", "## Prerequisites"):
                self.assertNotIn(banned, txt, f"{page.name} mixes how-to section: {banned}")

        md_targets = [ROOT / "README.md", ROOT / "AGENT.md", *sorted(DIATAXIS_DIR.rglob("*.md"))]
        for md in md_targets:
            _, blocks = _split_prose_and_code(md.read_text(encoding="utf-8"))
            text_no_code = md.read_text(encoding="utf-8")
            for _, _, _, body in blocks:
                if body:
                    text_no_code = text_no_code.replace(body, "")
            for raw_target in LINK_RE.findall(text_no_code):
                target = raw_target.strip().strip("<>").split()[0]
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_part = target.split("#", 1)[0]
                if not path_part:
                    continue
                resolved = (md.parent / path_part).resolve()
                self.assertTrue(resolved.exists(), f"Broken link in {md.relative_to(ROOT)}: {raw_target}")

    def test_ste_procedural_compliance_and_english_isolation(self) -> None:
        """Enforce STE sentence/modal limits on 02-how-to-guides and English-only fork artifacts."""
        howto_dir = DIATAXIS_DIR / "02-how-to-guides"
        for page in sorted(howto_dir.glob("*.md")):
            txt = page.read_text(encoding="utf-8")
            if page.name != "index.md":
                for section in ("**Prerequisites:**", "## Procedure", "## Verification", "## Rollback"):
                    self.assertIn(section, txt, f"{page.name} missing {section}")
                self.assertTrue("WARNING:" in txt or "CAUTION:" in txt, f"{page.name} needs WARNING or CAUTION")
            prose, _ = _split_prose_and_code(txt)
            for para, is_note in prose:
                self.assertNotIn(";", para, f"Semicolon prohibited in STE: {page.name}")
                self.assertFalse(FORBIDDEN_HOWTO_MODAL_RE.search(para), f"Forbidden modal/contraction in {page.name}: {para}")
                sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", para) if s.strip()]
                limit = 25 if is_note else 20
                for sent in sentences:
                    words = re.sub(r"`[^`]+`", "code", sent).split()
                    self.assertLessEqual(len(words), limit, f"STE sentence too long ({len(words)}>{limit}) in {page.name}: {sent}")

        for rel in ("build_rhel8.sh", "run_migration.sh"):
            content = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIsNone(FRENCH_LEAK_RE.search(content), f"French string found in {rel}")
        for md in sorted(DIATAXIS_DIR.rglob("*.md")):
            content = md.read_text(encoding="utf-8")
            self.assertIsNone(FRENCH_LEAK_RE.search(content), f"French string found in {md.relative_to(ROOT)}")

    def test_mermaid_diagrams_valid_and_zero_ascii_diagrams(self) -> None:
        """Verify zero ASCII box-arrow diagrams across Markdown files and compile Mermaid blocks when mmdc exists."""
        mmdc = _find_mmdc()
        mermaid_snippets: list[tuple[str, int, str]] = []

        for md in _iter_repo_markdowns():
            rel = md.relative_to(ROOT).as_posix()
            text = md.read_text(encoding="utf-8")
            _, blocks = _split_prose_and_code(text)
            for indent, lang, line, body in blocks:
                if lang == "mermaid":
                    self.assertEqual(indent, "", f"Indented Mermaid block in {rel}:{line}")
                    mermaid_snippets.append((rel, line, body))
                else:
                    self.assertIsNone(MERMAID_HEAD_RE.match(body), f"Untagged Mermaid header in {rel}:{line}")
                    is_tree = bool(re.search(r"[├└]─", body)) and not BARE_ARROW_RE.search(body) and not BOX_CHAR_RE.search(body)
                    if not is_tree:
                        has_box = bool(BOX_CHAR_RE.search(body))
                        has_arrow = bool(BARE_ARROW_RE.search(body))
                        self.assertFalse(has_box and (has_arrow or "+" in body), f"ASCII diagram left in {rel}:{line}")

        self.assertGreaterEqual(len(mermaid_snippets), 3)
        if mmdc is not None:
            with tempfile.TemporaryDirectory() as tmpdir:
                for idx, (rel, line, code) in enumerate(mermaid_snippets):
                    mmd_path = Path(tmpdir) / f"diag_{idx}.mmd"
                    svg_path = Path(tmpdir) / f"diag_{idx}.svg"
                    mmd_path.write_text(code + "\n", encoding="utf-8")
                    res = subprocess.run([mmdc, "-i", str(mmd_path), "-o", str(svg_path)], capture_output=True, text=True, timeout=60)
                    self.assertEqual(res.returncode, 0, f"mmdc failed on {rel}:{line}: {res.stderr}")

    def test_rhel8_scripts_dockerfile_and_version_parsing(self) -> None:
        """Validate RHEL8 build/migration scripts, Dockerfile, Makefile targets, and 3-digit C test artifacts."""
        dockerfile_rhel8 = (ROOT / "Dockerfile.rhel8").read_text(encoding="utf-8")
        for token in ("FROM rockylinux:8", "postgresql16-devel", "gc-devel", "make clean && make"):
            self.assertIn(token, dockerfile_rhel8)

        makefile_txt = (ROOT / "Makefile").read_text(encoding="utf-8")
        for target in ("bin:", "docs:", "update-docs:", "build:", "tests/*:"):
            self.assertIn(target, makefile_txt)

        parsing_c = (ROOT / "src" / "bin" / "pgcopydb" / "parsing_utils.c").read_text(encoding="utf-8")
        self.assertIn("Stop at the second dot", parsing_c)
        expected_out = (ROOT / "tests" / "unit" / "expected" / "9-version-parsing.out").read_text(encoding="utf-8")
        for ver in ("16.3", "18.1", "16.14.0", "18.3.10"):
            self.assertIn(ver, expected_out)

        if os.name == "posix" and shutil.which("bash"):
            for script in ("build_rhel8.sh", "run_migration.sh", "tests/unit/script/9-version-parsing.sh"):
                syn = subprocess.run(["bash", "-n", str(ROOT / script)], capture_output=True, text=True, timeout=15)
                self.assertEqual(syn.returncode, 0, f"bash -n failed for {script}: {syn.stderr}")
                self.assertNotIn("\r\n", (ROOT / script).read_text(encoding="utf-8"), f"CRLF found in {script}")

            for script in ("build_rhel8.sh", "run_migration.sh"):
                hlp = subprocess.run(["bash", str(ROOT / script), "--help"], capture_output=True, text=True, timeout=15)
                self.assertEqual(hlp.returncode, 0, f"{script} --help failed: {hlp.stderr}")
                self.assertIn("Usage:", hlp.stdout)

            # Verify run_migration.sh fails safely when URIs are unset (isolated temp copy without .env).
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_run = Path(tmpdir) / "run_migration.sh"
                tmp_run.write_text((ROOT / "run_migration.sh").read_text(encoding="utf-8"), encoding="utf-8")
                clean_env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
                guard = subprocess.run(["bash", str(tmp_run)], env=clean_env, capture_output=True, text=True, timeout=15)
                self.assertNotEqual(guard.returncode, 0)
                self.assertIn("[ERROR]", guard.stdout + guard.stderr)

            ver_run = subprocess.run(
                ["bash", str(ROOT / "tests" / "unit" / "script" / "9-version-parsing.sh")],
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(ver_run.returncode, 0)
            self.assertEqual(ver_run.stdout.strip(), expected_out.strip())

            gcc = shutil.which("gcc")
            pg_config = shutil.which("pg_config")
            if gcc and pg_config:
                pg_inc = subprocess.check_output([pg_config, "--includedir"], text=True).strip()
                cmd = [
                    gcc,
                    "-fsyntax-only",
                    "-std=c99",
                    f"-I{ROOT / 'src/bin/pgcopydb'}",
                    f"-I{ROOT / 'src/bin/lib/log/src'}",
                    f"-I{ROOT / 'src/bin/lib/libs'}",
                    f"-I{ROOT / 'src/bin/lib/pg'}",
                    f"-I{ROOT / 'src/bin/lib/parson'}",
                    f"-I{ROOT / 'src/bin/lib/subcommands.c'}",
                    f"-I{pg_inc}",
                    str(ROOT / "tests" / "unit" / "9-version-parsing.c"),
                ]
                c_check = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                self.assertEqual(c_check.returncode, 0, f"9-version-parsing.c syntax check failed: {c_check.stderr}")


if __name__ == "__main__":
    unittest.main()
