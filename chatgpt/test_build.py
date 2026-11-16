import filecmp, tempfile, unittest
from pathlib import Path

import build

REPO = build.REPO


class OneSkillsSource(unittest.TestCase):
    def test_built_skills_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = build.assemble(Path(tmp) / "pkg")
            built = sorted(p for p in (out / "skills").rglob("*") if p.is_file())
            self.assertTrue(built)
            for f in built:
                rel = f.relative_to(out / "skills")
                if rel.parts[-2:] == ("agents", "openai.yaml"):
                    continue
                src = REPO / "skills" / rel
                self.assertTrue(src.is_file(), f"{rel} is not in skills/")
                self.assertTrue(filecmp.cmp(src, f, shallow=False), f"{rel} differs from skills/")

    def test_no_chatgpt_only_skills(self):
        self.assertFalse((build.HERE / "skills").exists())


if __name__ == "__main__":
    unittest.main()
