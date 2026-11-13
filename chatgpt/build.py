#!/usr/bin/env python3
"""Assemble the ChatGPT directory package for Eric's New York and validate it.

Usage: python3 chatgpt/build.py   -> chatgpt/dist/erics-new-york-<version>.zip
Shared skills in ../skills are copied, never edited; text patches apply to the copy only.
"""
import json, shutil, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DIST = HERE / "dist"

# (skill, exact old text, new text): each must match exactly once or the build fails.
PATCHES = [(
    "attraction-pass-savings",
    "End with the link from the result where the user can check today's price and buy, and say that the figures are indicative.",
    "End with the link from the result where the user can check today's price, and say that the figures are indicative.",
)]
FORBIDDEN_WORDS = ["Claude"]  # must be absent from the shared skills


def yaml_str(s):
    return json.dumps(s, ensure_ascii=False)  # a JSON string is a valid YAML double-quoted scalar


def mcp_server():
    """(name, url) of the one server in chatgpt/mcp.json, the single source for the skills' dependency."""
    servers = json.loads((HERE / "mcp.json").read_text(encoding="utf-8"))["mcpServers"]
    if len(servers) != 1:
        sys.exit("build: mcp.json must declare exactly one server")
    (name, cfg), = servers.items()
    return name, cfg["url"]


def openai_yaml(meta):
    mcp_name, mcp_url = mcp_server()
    return (
        "interface:\n"
        f"  display_name: {yaml_str(meta['display_name'])}\n"
        f"  short_description: {yaml_str(meta['short_description'])}\n"
        "dependencies:\n"
        "  tools:\n"
        '    - type: "mcp"\n'
        f"      value: {yaml_str(mcp_name)}\n"
        '      description: "Eric\'s New York guide for planning a New York City trip"\n'
        '      transport: "streamable_http"\n'
        f"      url: {yaml_str(mcp_url)}\n"
    )


def assemble(out):
    """Build the plugin root at `out` (created fresh)."""
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    (out / "skills").mkdir(parents=True)
    (out / "assets").mkdir()
    for f in ("plugin.json", "mcp.json"):
        shutil.copy(HERE / f, out / f)
    shutil.copy(REPO / ".claude-plugin" / "icon.png", out / "assets" / "icon.png")

    sources = sorted(p for p in (REPO / "skills").iterdir() if p.is_dir()) + [HERE / "skills" / "omny-card"]
    for src in sources:
        shutil.copytree(src, out / "skills" / src.name, ignore=shutil.ignore_patterns(".*"))
    names = {p.name for p in (out / "skills").iterdir()}
    if len(names) != 16:
        sys.exit(f"build: expected 16 skills, found {len(names)}")

    for skill, old, new in PATCHES:
        f = out / "skills" / skill / "SKILL.md"
        text = f.read_text(encoding="utf-8")
        if text.count(old) != 1:
            sys.exit(f"build: patch for {skill} matched {text.count(old)} times, need exactly 1")
        f.write_text(text.replace(old, new), encoding="utf-8")

    for f in sorted((out / "skills").rglob("*")):
        if f.is_file() and f.suffix == ".md":
            text = f.read_text(encoding="utf-8")
            for w in FORBIDDEN_WORDS:
                if w in text:
                    sys.exit(f"build: '{w}' found in {f.relative_to(out)}")

    meta = json.loads((HERE / "skill-meta.json").read_text(encoding="utf-8"))
    if set(meta) != names:
        sys.exit(f"build: skill-meta.json differs from skills: {sorted(set(meta) ^ names)}")
    for name, m in meta.items():
        text = (out / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        h1 = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), None)
        if h1 != m["display_name"]:
            sys.exit(f"build: {name} display_name {m['display_name']!r} != H1 {h1!r}")
        (out / "skills" / name / "agents").mkdir()
        (out / "skills" / name / "agents" / "openai.yaml").write_text(openai_yaml(m), encoding="utf-8")
    return out


def make_zip(root, zip_path):
    """Deterministic ZIP: sorted file entries, fixed timestamps, plugin root at the archive root."""
    root, zip_path = Path(root), Path(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(p for p in root.rglob("*") if p.is_file()):
            zi = zipfile.ZipInfo(f.relative_to(root).as_posix(), (1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, f.read_bytes())
    return zip_path


def main():
    version = json.loads((HERE / "plugin.json").read_text(encoding="utf-8"))["version"]
    root = assemble(DIST / "erics-new-york")
    zp = make_zip(root, DIST / f"erics-new-york-{version}.zip")
    print(f"built {zp}")
    sys.path.insert(0, str(HERE))
    import validate
    return validate.main([str(zp)])


if __name__ == "__main__":
    sys.exit(main())
