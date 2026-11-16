import filecmp, tempfile, unittest
from pathlib import Path

import build

REPO = build.REPO


def relative_files(root):
    """Relative paths of the packaged files under root; dotfiles are excluded by design (see build.py)."""
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file() and not any(x.startswith(".") for x in p.relative_to(root).parts)}


class OneSkillsSource(unittest.TestCase):
    def test_built_skills_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = build.assemble(Path(tmp) / "pkg")
            source = relative_files(REPO / "skills")
            built = relative_files(out / "skills") - {p for p in relative_files(out / "skills") if p.parts[-2:] == ("agents", "openai.yaml")}
            self.assertTrue(built)
            self.assertEqual(source, built, "skills/ and the built skills list different files")
            for rel in built:
                self.assertTrue(filecmp.cmp(REPO / "skills" / rel, out / "skills" / rel, shallow=False), f"{rel} differs from skills/")

    def test_dotfiles_are_not_packaged(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = build.assemble(Path(tmp) / "pkg")
            self.assertFalse([p for p in relative_files(out / "skills") if any(part.startswith(".") for part in p.parts)])

    def test_no_chatgpt_only_skills(self):
        self.assertFalse((build.HERE / "skills").exists())


if __name__ == "__main__":
    unittest.main()
