import json, shutil, sys, tempfile, unittest, zipfile
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

    # ---- fix round: every case below fails on the pre-fix validator ----
    def edit_skill(self, r, fn, skill="omny-card", f="SKILL.md"):
        p = r / "skills" / skill / f
        p.write_text(fn(p.read_text()))

    def itf(self, **kw):
        return lambda r: plugin(r, lambda d: d["extensions"]["com.openai"]["interface"].update(**kw))

    def test_yaml_flow_value_front_matter(self):
        self.assertFails("fm1", "skill_frontmatter_yaml_unsupported",
                         lambda r: self.edit_skill(r, lambda t: t.replace("name: omny-card", "name: [", 1)))

    def test_yaml_unclosed_quote_agent(self):
        self.assertFails("ay1", "skill_agent_yaml_unsupported",
                         lambda r: self.edit_skill(r, lambda t: t.replace('display_name: "OMNY card"', 'display_name: "OMNY', 1), f="agents/openai.yaml"))

    def test_agent_plain_scalar_and_policy_ok(self):
        f = lambda r: self.edit_skill(r, lambda t: t.replace('display_name: "OMNY card"', "display_name: OMNY card", 1)
                                      + "policy:\n  products:\n    - CHAT\n  allow_implicit_invocation: true\n", f="agents/openai.yaml")
        self.assertEqual(self.run_mutant("ay2", f), [])

    def test_agent_bad_policy(self):
        self.assertFails("ay3", "skill_agent_policy_invalid",
                         lambda r: self.edit_skill(r, lambda t: t + "policy:\n  products:\n    - TABLET\n", f="agents/openai.yaml"))

    def corrupt_zip(self, name, mutate_bytes):
        z = build.make_zip(self.good, self.tmp / f"{name}.zip")
        with zipfile.ZipFile(z) as zf:
            i = zf.getinfo("assets/icon.png")
            off = i.header_offset + 30 + len(i.filename) + len(i.extra) + 100
        raw = bytearray(z.read_bytes()); raw[off] ^= 0xFF; z.write_bytes(bytes(raw))
        return validate.validate(z)[0]

    def test_corrupt_zip_member_reported(self):
        errs = self.corrupt_zip("crc", None)
        self.assertTrue(any("[archive_member_unreadable]" in e for e in errs), errs)

    def test_encrypted_member_reported(self):
        z = build.make_zip(self.good, self.tmp / "enc.zip")
        raw = bytearray(z.read_bytes())
        for sig, off in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
            p = 0
            while (p := raw.find(sig, p)) != -1:
                raw[p + off] |= 1; p += 4
        z.write_bytes(bytes(raw))
        errs = validate.validate(z)[0]
        self.assertTrue(any("[archive_member_unreadable]" in e for e in errs), errs)

    def test_mcp_root_list(self):
        self.assertFails("mcpl", "mcp_manifest_wrong_type", lambda r: (r / "mcp.json").write_text("[]"))

    def test_test_case_is_string(self):
        self.assertFails("tcs", "test_case_invalid",
                         lambda r: plugin(r, lambda d: d["extensions"]["com.openai"]["review"]["test_cases"]["positive"].__setitem__(0, "x")))

    def test_sibling_directory(self):
        top = self.tmp / "sib"
        shutil.copytree(self.good, top / "plugin")
        (top / "other").mkdir(); (top / "other" / "x.txt").write_text("x")
        errs = validate.validate(build.make_zip(top, self.tmp / "sib.zip"))[0]
        self.assertTrue(any("[plugin_root_has_siblings]" in e for e in errs), errs)

    def test_png_header_only(self):
        import struct
        fake = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 48, 48)
        self.assertFails("fakepng", "icon_not_png", lambda r: (r / "assets" / "icon.png").write_bytes(fake))

    def test_png_bad_chunk_crc(self):
        def f(r):
            p = r / "assets" / "icon.png"; b = bytearray(p.read_bytes()); b[40] ^= 0xFF; p.write_bytes(bytes(b))
        self.assertFails("pngcrc", "icon_not_png", f)

    def test_multiline_names(self):
        self.assertFails("dnl", "display_name_multiline", self.itf(displayName="Eric's\nNY"))
        self.assertFails("dvl", "developer_name_multiline", self.itf(developerName="New York\nMedia"))

    def test_blank_and_multiline_capabilities(self):
        self.assertFails("cap1", "capabilities_invalid", self.itf(capabilities=["   "]))
        self.assertFails("cap2", "capabilities_invalid", self.itf(capabilities=["two\nlines"]))

    def test_prompts_unique_after_normalisation(self):
        self.assertFails("dp", "default_prompt_invalid", self.itf(defaultPrompt=["Same prompt", "SAME  prompt"]))

    def test_onboarding_skill_must_exist(self):
        self.assertFails("onb", "onboarding_skill_invalid",
                         lambda r: plugin(r, lambda d: d["extensions"]["com.openai"].update(onboardingSkill="./skills/nope/SKILL.md")))

    def test_root_description_wording(self):
        self.assertFails("rdw", "wording_pricing", lambda r: plugin(r, lambda d: d.update(description="Great prices for New York.")))

    def test_good_yaml_parses_in_build(self):
        name, url = build.mcp_server()
        self.assertEqual((name, url), ("erics-new-york", "https://ericsnewyork.com/mcp"))


if __name__ == "__main__":
    unittest.main()
