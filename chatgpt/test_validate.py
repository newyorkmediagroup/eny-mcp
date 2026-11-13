import json, shutil, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build, validate


def plugin(root, fn):
    p = Path(root) / "plugin.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    fn(d)
    p.write_text(json.dumps(d), encoding="utf-8")


class ValidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.good = build.assemble(cls.tmp / "good")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def run_mutant(self, name, mutate):
        root = self.tmp / name
        shutil.copytree(self.good, root)
        mutate(root)
        return validate.validate(build.make_zip(root, self.tmp / f"{name}.zip"))[0]

    def assertFails(self, name, code, mutate):
        errs = self.run_mutant(name, mutate)
        self.assertTrue(any(f"[{code}]" in e for e in errs), f"{code} not reported; got {errs}")

    def test_good_zip_passes(self):
        errs, notes, owner = validate.validate(build.make_zip(self.good, self.tmp / "good.zip"))
        self.assertEqual(errs, [])
        self.assertEqual(len(owner), 1)

    def test_submit_needs_owner_item(self):
        errs, _, _ = validate.validate(self.tmp / "good.zip" if (self.tmp / "good.zip").exists() else build.make_zip(self.good, self.tmp / "good.zip"), submit=True)
        self.assertTrue(any("[owner_item_missing]" in e for e in errs))

    def test_zip_is_deterministic(self):
        a = build.make_zip(self.good, self.tmp / "a.zip").read_bytes()
        b = build.make_zip(self.good, self.tmp / "b.zip").read_bytes()
        self.assertEqual(a, b)

    def test_display_name_31_chars(self):
        self.assertFails("dn", "display_name_too_long",
                         lambda r: plugin(r, lambda d: d["extensions"]["com.openai"]["interface"].update(displayName="x" * 31)))

    def test_four_positive_cases(self):
        self.assertFails("pos4", "test_cases_positive_count",
                         lambda r: plugin(r, lambda d: d["extensions"]["com.openai"]["review"]["test_cases"]["positive"].pop()))

    def test_missing_icon(self):
        self.assertFails("noicon", "icon_missing", lambda r: (r / "assets" / "icon.png").unlink())

    def test_http_privacy_url(self):
        self.assertFails("http", "listing_url_invalid",
                         lambda r: plugin(r, lambda d: d["extensions"]["com.openai"]["interface"].update(privacyPolicyURL="http://ericsnewyork.com/privacy/")))

    def test_skill_without_front_matter(self):
        f = lambda r: (r / "skills" / "omny-card" / "SKILL.md").write_text("# OMNY card\n\nBody only.\n")
        self.assertFails("nofm", "skill_frontmatter_missing", f)

    def test_app_json_added(self):
        self.assertFails("app", "forbidden_component", lambda r: (r / ".app.json").write_text("{}"))

    def test_tool_not_live_in_test_case(self):
        self.assertFails("tool", "tool_not_live",
                         lambda r: plugin(r, lambda d: d["extensions"]["com.openai"]["review"]["test_cases"]["positive"][0].update(tools_triggered="book_ticket")))

    def test_tool_not_live_in_skill_body(self):
        def f(r):
            p = r / "skills" / "omny-card" / "SKILL.md"
            p.write_text(p.read_text().replace("`get_omny_card_info`", "`get_omny_card_infos`", 1))
        self.assertFails("skilltool", "tool_not_live", f)

    def test_vegas_is_rejected(self):
        def f(r):
            p = r / "skills" / "omny-card" / "SKILL.md"
            p.write_text(p.read_text() + "\nAlso " + "Las Ve" + "gas.\n")
        self.assertFails("vegas", "vegas_mention", f)


if __name__ == "__main__":
    unittest.main()
