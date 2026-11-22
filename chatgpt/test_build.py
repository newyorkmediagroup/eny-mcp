import filecmp, json, tempfile, unittest
from pathlib import Path

import build

REPO = build.REPO


def relative_files(root):
    """Relative paths of the packaged files under root; dotfiles are excluded by design (see build.py)."""
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file() and not any(x.startswith(".") for x in p.relative_to(root).parts)}


class OneSkillsSource(unittest.TestCase):
    def test_built_skills_are_verbatim_except_listed_edits(self):
        edits = json.loads((build.HERE / "skill-edits.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            out = build.assemble(Path(tmp) / "pkg")
            source = {p for p in relative_files(REPO / "skills") if p.parts[0] not in build.NOT_SHIPPED}
            built = relative_files(out / "skills") - {p for p in relative_files(out / "skills") if p.parts[-2:] == ("agents", "openai.yaml")}
            self.assertTrue(built)
            self.assertEqual(source, built, "skills/ and the built skills list different files")
            for rel in built:
                if rel.as_posix() in edits:
                    text = (REPO / "skills" / rel).read_text(encoding="utf-8")
                    for e in edits[rel.as_posix()]:
                        text = text.replace(e["old"], e["new"], 1)
                    self.assertEqual((out / "skills" / rel).read_text(encoding="utf-8"), text, f"{rel} is not the source plus its listed edits")
                else:
                    self.assertTrue(filecmp.cmp(REPO / "skills" / rel, out / "skills" / rel, shallow=False), f"{rel} differs from skills/")

    def test_edit_must_match_exactly_once(self):
        path = "omny-card/SKILL.md"
        for old in ("text that is not in the skill", "the"):
            with self.subTest(old=old), tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
                build.assemble(Path(tmp) / "pkg", {path: [{"old": old, "new": "x"}]})

    def test_no_unprompted_social_or_newsletter_invitation(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = build.assemble(Path(tmp) / "pkg")
            plan = (out / "skills" / "plan-a-first-trip" / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("follow Eric's New York on social", plan)
            self.assertNotIn("join the newsletter", plan)
            steps = [l.split(".")[0] for l in plan.splitlines() if l[:1].isdigit()]
            self.assertEqual(steps, [str(i) for i in range(1, len(steps) + 1)])

    def test_dotfiles_are_not_packaged(self):
        probe = next(p for p in sorted((REPO / "skills").iterdir()) if p.is_dir()) / ".probe-dotfile"
        probe.write_text("x")
        try:
            with tempfile.TemporaryDirectory() as tmp:
                out = build.assemble(Path(tmp) / "pkg")
                raw = [p.name for p in (out / "skills").rglob("*")]
                self.assertNotIn(".probe-dotfile", raw)
        finally:
            probe.unlink()

    def test_not_shipped_skill_is_absent_and_the_rest_ship(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = build.assemble(Path(tmp) / "pkg")
            shipped = {p.name for p in (out / "skills").iterdir()}
            self.assertFalse(shipped & build.NOT_SHIPPED)
            self.assertEqual(shipped, {p.name for p in (REPO / "skills").iterdir() if p.is_dir()} - build.NOT_SHIPPED)
            self.assertEqual(len(shipped), 15)

    def test_no_chatgpt_only_skills(self):
        self.assertFalse((build.HERE / "skills").exists())


if __name__ == "__main__":
    unittest.main()
