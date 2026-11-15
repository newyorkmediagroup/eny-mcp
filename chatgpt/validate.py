#!/usr/bin/env python3
"""Validate a ChatGPT plugin ZIP against OpenAI's published rules (stdlib only).

Usage: python3 chatgpt/validate.py <zip> [--submit] [--tools <tools-list.json>]
Exit 0 = ready for review except owner items. With --submit, also fails on items only the owner can supply.
Upload itself accepts partial test-case lists (SUB:649); this validator deliberately enforces the 5+3 cases that
review needs, so it is stricter than upload. It is also intentionally stricter than OpenAI on YAML (no YAML
library here): only the simple shapes the builder emits are accepted, anything else is *_yaml_unsupported.
Images: PNG only (JPEG/WebP/SVG are valid for OpenAI but not decoded here).

Rule sources, all under tasks/WD-4138-evidence/openai-pages/ (cited as file:line):
  SUB = plugins_deploy_submission.md    ERR = plugins_deploy_submission-errors.md
  GUI = plugins_plugin-guidelines.md    SKL = plugins_build_skills.md
  SCHEMA = chatgpt/schemas/{plugin,mcp}.schema.json (copies of plugin.schema.json / mcp.schema.json)
"""
import json, re, struct, sys, unicodedata, zipfile, zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS_DEFAULT = HERE / "tools-list.json"
MiB = 1024 * 1024
CATEGORIES = ["Productivity", "Creativity", "Developer Tools", "Business & Operations", "Data & Analytics",
              "Communication", "Education & Research", "Security", "Finance", "Healthcare", "Travel",
              "Entertainment", "Other"]  # ERR:240
TOOL_VERBS = {"get", "list", "search", "calculate", "send", "nearest", "site", "new"}
SECRET_RES = [r"sk-[A-Za-z0-9]{20,}", r"ghp_[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{12,}", r"xox[baprs]-[A-Za-z0-9-]{10,}",
              r"-----BEGIN [A-Z ]*PRIVATE KEY", r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{20,}",
              r"(?i)\b(api[_-]?key|secret|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9]{12,}"]


# ---------- minimal JSON-schema validator (type, const, enum, required, properties, ----------
# ---------- additionalProperties, pattern, minLength, maxLength, items, oneOf, $ref, not) ----------
def _type_ok(v, t):
    return {"object": isinstance(v, dict), "array": isinstance(v, list), "string": isinstance(v, str)}.get(t, True)


def schema_check(v, s, root, path="$"):
    if "$ref" in s:
        node = root
        for part in s["$ref"].lstrip("#/").split("/"):
            node = node[part]
        return schema_check(v, node, root, path)
    errs = []
    if "oneOf" in s:
        good = [schema_check(v, sub, root, path) for sub in s["oneOf"]]
        if sum(1 for e in good if not e) != 1:
            return [f"{path}: must match exactly one of the server types"]
        return []
    if "not" in s:
        if not schema_check(v, s["not"], root, path):
            errs.append(f"{path}: value not allowed")
        return errs
    if "const" in s and v != s["const"]:
        errs.append(f"{path}: must be {s['const']!r}")
    if "enum" in s and v not in s["enum"]:
        errs.append(f"{path}: must be one of {s['enum']}")
    if "type" in s and not _type_ok(v, s["type"]):
        return errs + [f"{path}: must be {s['type']}"]
    if isinstance(v, str):
        if len(v) < s.get("minLength", 0):
            errs.append(f"{path}: shorter than {s['minLength']}")
        if len(v) > s.get("maxLength", 10**9):
            errs.append(f"{path}: longer than {s['maxLength']}")
        if "pattern" in s and not re.search(s["pattern"], v):
            errs.append(f"{path}: does not match pattern {s['pattern']}")
    if isinstance(v, list) and "items" in s:
        for i, x in enumerate(v):
            errs += schema_check(x, s["items"], root, f"{path}[{i}]")
    if isinstance(v, dict):
        for r in s.get("required", []):
            if r not in v:
                errs.append(f"{path}: missing required '{r}'")
        props = s.get("properties", {})
        for k, x in v.items():
            if "propertyNames" in s:
                errs += schema_check(k, s["propertyNames"], root, f"{path}.{k}(name)")
            if k in props:
                errs += schema_check(x, props[k], root, f"{path}.{k}")
            elif s.get("additionalProperties") is False:
                errs.append(f"{path}: unknown property '{k}'")
            elif isinstance(s.get("additionalProperties"), dict):
                errs += schema_check(x, s["additionalProperties"], root, f"{path}.{k}")
    return errs


# ---------- helpers ----------
def png_info(data):
    """(width, height) of a PNG whose chunk CRCs all verify and that has IHDR, IDAT and IEND; else None."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    pos, kinds, dims = 8, [], None
    while pos + 12 <= len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body, crc = data[pos + 8:pos + 8 + ln], data[pos + 8 + ln:pos + 12 + ln]
        if len(body) != ln or len(crc) != 4 or struct.unpack(">I", crc)[0] != zlib.crc32(typ + body):
            return None
        if not kinds and (typ != b"IHDR" or ln != 13):
            return None
        if typ == b"IHDR":
            dims = struct.unpack(">II", body[:8])
        kinds.append(typ)
        pos += 12 + ln
        if typ == b"IEND":
            break
    return dims if dims and b"IDAT" in kinds and kinds[-1] == b"IEND" else None


def https_ok(u, limit):
    from urllib.parse import urlsplit
    if not isinstance(u, str):
        return False
    p = urlsplit(u)
    return p.scheme == "https" and bool(p.hostname) and not p.username and not p.password and len(u) <= limit


def one_line(v):
    return "\n" not in v and "\r" not in v


def norm_text(p):
    return " ".join(unicodedata.normalize("NFKC", p).split()).casefold()


def yaml_scalar(s):
    """One simple YAML scalar: "double", 'single' or plain text. Anything fancier raises ValueError."""
    s = s.strip()
    if s == "":
        return ""
    if s[0] == '"':
        try:
            v = json.loads(s)
        except ValueError:
            raise ValueError(f"bad double-quoted string {s[:40]!r}")
        if not isinstance(v, str):
            raise ValueError(f"bad double-quoted string {s[:40]!r}")
        return v
    if s[0] == "'":
        if not re.fullmatch(r"'(?:[^']|'')*'", s):
            raise ValueError(f"bad single-quoted string {s[:40]!r}")
        return s[1:-1].replace("''", "'")
    if s[0] in "[{|>&*!%@`#,?\"'" or s.startswith("- ") or ": " in s or " #" in s or s.endswith(":"):
        raise ValueError(f"unsupported value {s[:40]!r}")
    low = s.lower()
    if low in ("true", "yes", "on"): return True   # YAML reads these as non-strings
    if low in ("false", "no", "off"): return False
    if low in ("null", "~"): return None
    if re.fullmatch(r"[-+]?[\d_]*\.?\d+([eE][-+]?\d+)?", s): return 0
    return s


KEY_LINE = re.compile(r"([A-Za-z_][\w-]*):(?: +(.*))?")


def front_matter(text):
    """((mapping, body), None); (None, 'missing'|'unclosed'); raises ValueError on non-simple YAML."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, "missing"
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm = {}
            for l in lines[1:i]:
                if not l.strip() or l.lstrip().startswith("#"):
                    continue
                m = KEY_LINE.fullmatch(l.rstrip())
                if not m or l[0] == " " or m.group(1) in fm:
                    raise ValueError(f"unsupported front-matter line {l[:60]!r}")
                fm[m.group(1)] = yaml_scalar(m.group(2) or "")
            return (fm, "\n".join(lines[i + 1:])), None
    return None, "unclosed"


def parse_agent_yaml(text):
    """Strict reader for the agents/openai.yaml shapes: interface, policy, dependencies.tools[]."""
    out, sec, sub = {}, None, None
    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        ind, body = len(line) - len(line.lstrip(" ")), line.strip()
        bad = ValueError(f"unsupported line {line[:60]!r}")
        if "\t" in line:
            raise bad
        if ind == 0:
            m = re.fullmatch(r"([A-Za-z_][\w-]*):", body)
            if not m or m.group(1) in out:
                raise bad
            sec, sub = m.group(1), None
            out[sec] = {}
        elif sec is None:
            raise bad
        elif ind == 2:
            m = KEY_LINE.fullmatch(body)
            if not m:
                raise bad
            k, v = m.groups()
            if not v:
                if (sec, k) not in (("dependencies", "tools"), ("policy", "products"), ("interface", k)):
                    raise bad
                out[sec][k], sub = ([] if sec != "interface" else ""), (k if sec != "interface" else None)
            else:
                out[sec][k], sub = yaml_scalar(v), None
        elif ind == 4:
            if sub is None or not body.startswith("- "):
                raise bad
            item = body[2:]
            if sec == "policy":
                out[sec][sub].append(yaml_scalar(item))
            elif sec == "dependencies":
                m = KEY_LINE.fullmatch(item)
                if not m or not m.group(2):
                    raise bad
                out[sec][sub].append({m.group(1): yaml_scalar(m.group(2))})
            else:
                raise bad
        elif ind == 6 and sec == "dependencies" and sub == "tools" and out[sec][sub]:
            m = KEY_LINE.fullmatch(body)
            if not m or not m.group(2):
                raise bad
            out[sec][sub][-1][m.group(1)] = yaml_scalar(m.group(2))
        else:
            raise bad
    return out


def load_tools(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    d = d.get("tools", d) if isinstance(d, dict) else d
    return {t["name"] for t in d}


# ---------- main validation ----------
def validate(zip_path, submit=False, tools_path=TOOLS_DEFAULT):
    E, N, OWNER = [], [], []
    err = lambda code, msg: E.append(f"[{code}] {msg}")
    tools = load_tools(tools_path)
    zp = Path(zip_path)
    if not zp.is_file() or zp.stat().st_size == 0:
        return [f"[archive_empty] no ZIP or empty (ERR:119)"], N, OWNER
    if zp.stat().st_size > 100 * MiB:
        err("archive_too_large", "compressed ZIP over 100 MB (ERR:120)")
    try:
        z = zipfile.ZipFile(zp)
    except (zipfile.BadZipFile, OSError, EOFError):
        return ["[archive_format_not_zip] not a valid ZIP (ERR:121)"], N, OWNER
    infos = z.infolist()
    if not infos:
        return ["[archive_empty] archive has no entries (ERR:119)"], N, OWNER
    if len(infos) > 5000:
        err("archive_too_many_entries", "over 5,000 entries (ERR:135)")
    if sum(i.file_size for i in infos) > 512 * MiB:
        err("archive_uncompressed_too_large", "over 512 MiB extracted (ERR:136)")
    seen, norm = set(), {}
    for i in infos:
        n = i.filename
        segs = n.rstrip("/").split("/")
        if not n.strip("/"): err("archive_member_path_empty", "empty path (ERR:122)")
        if n != n.strip(): err("archive_member_path_has_outer_whitespace", repr(n) + " (ERR:123)")
        if "\\" in n: err("archive_member_path_has_backslash", n + " (ERR:124)")
        if n.startswith("/"): err("archive_member_path_absolute", n + " (ERR:125)")
        if "" in segs: err("archive_member_path_has_empty_segment", n + " (ERR:126)")
        if ".." in segs: err("archive_member_path_has_parent_segment", n + " (ERR:127)")
        if len(segs) > 20: err("archive_member_path_too_deep", n + " (ERR:128)")
        if i.file_size > 100 * MiB: err("archive_member_too_large", n + " (ERR:132)")
        if i.flag_bits & 1: err("archive_member_unreadable", n + " is encrypted (ERR:137)")
        if (i.external_attr >> 16) & 0o170000 == 0o120000: err("archive_member_type_unsupported", n + " is a symlink (ERR:131)")
        if n in seen: err("archive_member_path_duplicate", n + " (ERR:133)")
        seen.add(n)
        key = unicodedata.normalize("NFC", n).casefold()
        if key in norm and norm[key] != n: err("archive_member_path_normalization_collision", n + " (ERR:130)")
        norm[key] = n
    # read every member once: this also CRC-checks it; unreadable members are reported, never raised
    data = {}
    for i in infos:
        if i.filename.endswith("/") or i.flag_bits & 1 or i.file_size > 100 * MiB:
            continue
        try:
            data[i.filename] = z.read(i)
        except (zipfile.BadZipFile, RuntimeError, zlib.error, OSError, EOFError, NotImplementedError) as e:
            err("archive_member_unreadable", f"{i.filename}: {type(e).__name__}: {e} (ERR:137)")
    names = list(data)

    # plugin root (ERR:145-146)
    if "plugin.json" in names:
        prefix = ""
    else:
        tops = {n.split("/")[0] for n in names}
        cand = [t for t in tops if f"{t}/plugin.json" in names]
        if len(cand) != 1:
            err("plugin_root_ambiguous", "need exactly one plugin root with plugin.json (ERR:145)")
            return E, N, OWNER
        prefix = cand[0] + "/"
        for n in names:
            if not n.startswith(prefix):
                err("plugin_root_has_siblings", f"{n} is outside the top-level plugin directory (ERR:146)")
    rel = {n[len(prefix):]: n for n in names if n.startswith(prefix)}
    read = lambda r: data[rel[r]]

    # components that must not ship (ERR:110-111; hooks per WD-4138 brief)
    for r in rel:
        top = r.split("/")[0]
        if r in (".app.json", ".mcp.json") or top in (".claude-plugin", ".codex-plugin", ".agent-plugin", "hooks") or r == "hooks.json":
            err("forbidden_component", f"{r} must not be in the package (ERR:109-111)")

    # no Las Vegas, no secrets (WD-4138 brief)
    for n in names:
        raw = data[n]
        if b"vegas" in raw.lower():
            err("vegas_mention", f"{n} mentions Vegas")
        if n.endswith((".json", ".md", ".yaml", ".txt")):
            t = raw.decode("utf-8", "replace")
            for rx in SECRET_RES:
                if re.search(rx, t):
                    err("secret_like_string", f"{n} matches {rx}")

    # plugin.json
    try:
        pj = json.loads(read("plugin.json").decode("utf-8"))
        assert isinstance(pj, dict)
    except Exception as e:
        err("plugin_manifest_json_malformed", f"plugin.json: {e} (ERR:155-156)")
        return E, N, OWNER
    s = json.loads((HERE / "schemas" / "plugin.schema.json").read_text())
    for m in schema_check(pj, s, s, "plugin.json"):
        err("plugin_schema", m + " (SCHEMA plugin)")
    name = pj.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(name)) or len(str(name)) > 64:
        err("plugin_name_format", "name must be <=64 lowercase letters, digits, single hyphens (SUB:565)")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", str(pj.get("version", ""))) or len(str(pj.get("version", ""))) > 64:
        err("plugin_version_not_semver", "version must be semver (ERR:166-170)")
    d = pj.get("description")
    if not isinstance(d, str) or not d or len(d) > 1024:
        err("plugin_description_length", "description required, <=1024 chars (ERR:171-174)")
    a = pj.get("author", {}) if isinstance(pj.get("author"), dict) else {}
    if not isinstance(a.get("name"), str) or not a["name"] or len(a["name"]) > 120: err("plugin_author_name", "author.name required, <=120 (ERR:176-180)")
    if not isinstance(a.get("email", ""), str) or len(a.get("email", "")) > 320: err("plugin_author_email_too_long", "<=320 (ERR:184)")
    if "url" in a and not https_ok(a["url"], 2048): err("plugin_author_url", "author.url must be https, no credentials, <=2048 (ERR:188-190)")
    if "homepage" in pj and not https_ok(pj["homepage"], 2048): err("plugin_homepage_format", "homepage must be https <=2048 (ERR:266-267)")

    ox = (pj.get("extensions") or {}).get("com.openai")
    if not isinstance(ox, dict):
        err("openai_extension_missing", "extensions.com.openai is required (SUB:573)")
        return E, N, OWNER
    for k in ox:
        if k not in ("interface", "id", "onboardingSkill", "review", "publication"):
            err("openai_extension_unknown_key", f"extensions.com.openai.{k} (SUB:577-582, 620)")
    if "test_credentials" in json.dumps(pj) or "reviewer_instructions" in json.dumps(pj):
        err("review_secrets_in_package", "test_credentials / reviewer_instructions are rejected (SUB:655)")

    # interface (SUB:590-610; short limits are the SUBMISSION limits, ERR:223-280)
    itf = ox.get("interface") if isinstance(ox.get("interface"), dict) else {}
    def sfield(k, lim, code):
        v = itf.get(k)
        if not isinstance(v, str) or not v.strip():
            err(code, f"interface.{k} required (SUB:590-601)")
        elif len(v) > lim:
            err(code + "_too_long", f"interface.{k} is {len(v)} chars, limit {lim} (SUB:{ {'displayName':592,'shortDescription':593,'longDescription':594,'developerName':595}[k] })")
        return v or ""
    dn = sfield("displayName", 30, "display_name")
    sd = sfield("shortDescription", 30, "short_description")
    ld = sfield("longDescription", 4000, "long_description")
    sfield("developerName", 80, "developer_name")
    if not one_line(sd): err("short_description_multiline", "must fit on one line (ERR:225)")
    for k, code in (("displayName", "display_name_multiline"), ("developerName", "developer_name_multiline")):
        if isinstance(itf.get(k), str) and not one_line(itf[k]): err(code, f"interface.{k} must fit on one line (ERR:31-34)")
    if itf.get("category") not in CATEGORIES: err("category_unknown", f"category must be one of {CATEGORIES} (ERR:240)")
    caps = itf.get("capabilities", [])
    if not isinstance(caps, list) or len(caps) > 20 or any(not isinstance(c, str) or not c.strip() or len(c) > 120 or not one_line(c) for c in caps):
        err("capabilities_invalid", "<=20 non-blank one-line strings of <=120 chars (ERR:36)")
    for k in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        if not isinstance(itf.get(k), str) or not https_ok(itf[k], 1024):
            err("listing_url_invalid", f"interface.{k} must be present, https, <=1024, no credentials (SUB:598-610)")
    dp = itf.get("defaultPrompt", [])
    dp = [dp] if isinstance(dp, str) else dp
    if not isinstance(dp, list) or len(dp) > 3 or any(not isinstance(p, str) or not norm_text(p) or len(p) > 128 or not one_line(p) or "@" in p for p in dp) \
            or len({norm_text(p) for p in dp}) != len(dp):
        err("default_prompt_invalid", "<=3 prompts, unique after NFKC + whitespace + case normalization, one line, <=128 chars, no '@' (SUB:602, ERR:37)")
    if "onboardingSkill" in ox:
        ob = ox["onboardingSkill"]
        if not isinstance(ob, str) or not ob.startswith("./") or ob[2:] not in rel or not ob.endswith("/SKILL.md"):
            err("onboarding_skill_invalid", "onboardingSkill must be a ./-prefixed path to a SKILL.md inside the package (SUB:622)")
    for k in ("brandColor", "brandColorDark"):
        if k in itf and not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(itf[k])): err("brand_color_format", f"{k} must be #RRGGBB (ERR:270)")
    # icons (SUB:612-616, ERR:396-431)
    for k in ("composerIcon", "logo"):
        p = itf.get(k)
        if not isinstance(p, str) or not p.startswith("./"):
            err("icon_path_invalid", f"interface.{k} must be a ./-prefixed path (ERR:402)"); continue
        r = p[2:]
        if r not in rel:
            err("icon_missing", f"interface.{k} points to {p}, which is not in the package (ERR:405, 415-416)"); continue
        raw = read(r)
        info = png_info(raw) if r.lower().endswith(".png") else None
        if info is None:
            err("icon_not_png", f"{r}: must be a PNG with IHDR, IDAT, IEND and valid chunk CRCs; PNG-only is a limit of this validator, OpenAI also accepts JPEG/WebP/SVG (ERR:419-421)")
        else:
            w, h = info
            if w != h: err("icon_not_square", f"{r} is {w}x{h} (ERR:422)")
            if w < 48 or h < 48: err("icon_too_small", f"{r} is {w}x{h}, min 48 (ERR:423)")
            if w > 4096 or h > 4096: err("icon_too_large_dimensions", f"{r} is {w}x{h}, max 4096 (ERR:424)")
        if len(raw) > 5 * MiB: err("icon_too_large_bytes", f"{r} over 5 MiB (ERR:418)")
    # wording (GUI:40-42, GUI:198)
    for label, t in (("description", d if isinstance(d, str) else ""), ("displayName", dn), ("shortDescription", sd), ("longDescription", ld)):
        if re.search(r"\bMCP\b", t): err("wording_mcp", f"{label} contains 'MCP' (GUI:40)")
        if re.search(r"(?i)\b(best|official)\b", t): err("wording_promotional", f"{label} contains best/official (GUI:198)")
        if re.search(r"(?i)\b(prices?|pricing|discounts?|free trials?|promotions?|subscriptions?)\b", t):
            err("wording_pricing", f"{label} mentions price/discount/trial words (GUI:42)")
    if re.search(r"(?i)plugin\s*$", dn): err("wording_plugin_suffix", "displayName must not end in 'Plugin' (GUI:40)")

    # review (SUB:624-655)
    rv = ox.get("review") if isinstance(ox.get("review"), dict) else {}
    tc = rv.get("test_cases") if isinstance(rv.get("test_cases"), dict) else {}
    pos, neg = tc.get("positive", []), tc.get("negative", [])
    if not isinstance(pos, list) or len(pos) != 5: err("test_cases_positive_count", f"review needs exactly 5 positive cases, found {len(pos) if isinstance(pos, list) else '?'} (SUB:649)")
    if not isinstance(neg, list) or len(neg) != 3: err("test_cases_negative_count", f"review needs exactly 3 negative cases, found {len(neg) if isinstance(neg, list) else '?'} (SUB:649)")
    for i, c in enumerate(pos if isinstance(pos, list) else []):
        if not isinstance(c, dict): err("test_case_invalid", f"positive[{i}] must be an object (SUB:642)"); continue
        for k in ("description", "prompt", "tools_triggered", "expected_behavior"):
            if not isinstance(c.get(k), str) or not c[k].strip(): err("test_case_field_missing", f"positive[{i}].{k} required (SUB:642-645)")
        for t in str(c.get("tools_triggered", "")).split(","):
            if t.strip() and t.strip() not in tools: err("tool_not_live", f"positive[{i}] names tool '{t.strip()}' which is not in the live tools list")
    for i, c in enumerate(neg if isinstance(neg, list) else []):
        if not isinstance(c, dict): err("test_case_invalid", f"negative[{i}] must be an object (SUB:642)"); continue
        for k in ("description", "prompt"):
            if not isinstance(c.get(k), str) or not c[k].strip(): err("test_case_field_missing", f"negative[{i}].{k} required (SUB:642-643)")
    if not isinstance(rv.get("commerce"), bool): err("commerce_missing", "review.commerce must be a boolean (SUB:630)")
    if rv.get("commerce") and not rv.get("commerce_description"): err("commerce_description_missing", "commerce true needs commerce_description (SUB:631)")
    if "demo_recording_url" in rv:
        if not https_ok(str(rv["demo_recording_url"]), 2048): err("demo_recording_url_invalid", "must be https (SUB:629)")
    else:
        OWNER.append("review.demo_recording_url - reviewer-accessible video walkthrough; required for MCP review (SUB:629)")
        if submit: err("owner_item_missing", "review.demo_recording_url missing (SUB:629)")
    pub = ox.get("publication") if isinstance(ox.get("publication"), dict) else {}
    if "countries" not in pub: N.append("publication.countries omitted: existing targeting preserved, owner decides (SUB:632)")
    trs = pub.get("translations") if isinstance(pub.get("translations"), dict) else {}
    for loc, t in trs.items():
        if not isinstance(t, dict): err("translation_invalid", f"{loc} must be an object (SUB:635)"); continue
        if len(str(t.get("subtitle") or "")) > 30 or len(str(t.get("description") or "")) > 4000: err("translation_too_long", f"{loc} (SUB:635-636)")

    # mcp.json (SCHEMA mcp; SUB:649 one server; no credentials)
    try:
        mj = json.loads(read("mcp.json").decode("utf-8"))
    except Exception as e:
        err("mcp_manifest_invalid", f"mcp.json: {e} (ERR:314-315)"); mj = {}
    if not isinstance(mj, dict):
        err("mcp_manifest_wrong_type", "mcp.json must be a JSON object at the top level (ERR:316)"); mj = {}
    else:
        ms = json.loads((HERE / "schemas" / "mcp.schema.json").read_text())
        for m in schema_check(mj, ms, ms, "mcp.json"):
            err("mcp_schema", m + " (SCHEMA mcp)")
    srv = mj.get("mcpServers", {}) if isinstance(mj.get("mcpServers"), dict) else {}
    if len(srv) != 1: err("mcp_server_count", "plugin-level test cases need exactly one MCP server (SUB:649)")
    for n_, sv in srv.items():
        if not isinstance(sv, dict): continue
        if "url" in sv and not https_ok(sv["url"], 2048): err("mcp_url_invalid", f"{n_}: url must be https with no credentials (SUB:610)")
        if sv.get("headers"): err("mcp_headers_present", f"{n_}: headers can carry secrets; this server needs none")
    N.append("upload through the With MCP route (submission.md:17,31)")

    # skills (ERR:322-392, SKL:92-113)
    skill_dirs = sorted({r.split("/")[1] for r in rel if r.startswith("skills/") and r.count("/") >= 2})
    if not skill_dirs: err("runtime_surface_missing", "at least one valid skill is required (ERR:144, 302)")
    sk_names = {}
    for sd_ in skill_dirs:
        if sd_.startswith("."): err("skill_directory_hidden", sd_ + " (ERR:328)")
        mdp = f"skills/{sd_}/SKILL.md"
        if mdp not in rel: err("skill_manifest_missing", f"{sd_} has no SKILL.md (ERR:326)"); continue
        try: text = read(mdp).decode("utf-8")
        except UnicodeDecodeError: err("skill_manifest_invalid_utf8", mdp + " (ERR:332)"); continue
        try: fm, why = front_matter(text)
        except ValueError as e: err("skill_frontmatter_yaml_unsupported", f"{mdp}: {e} (ERR:333-340)"); continue
        if fm is None: err("skill_frontmatter_" + why, f"{mdp} (ERR:333-334)"); continue
        meta, body = fm
        for k, code in (("name", "skill_name"), ("description", "skill_description")):
            if k in meta and not isinstance(meta[k], str): err(code + "_not_string", f"{mdp} {k} must be a string (ERR:338, 342)")
        if not meta.get("name"): err("skill_name_missing", mdp + " (ERR:337)")
        if not meta.get("description"): err("skill_description_missing", mdp + " (ERR:341)")
        elif isinstance(meta["description"], str) and len(meta["description"]) > 1024: err("skill_description_too_long", mdp + " (ERR:344)")
        if not body.strip(): err("skill_body_empty", mdp + " (ERR:346)")
        nm = meta.get("name") if isinstance(meta.get("name"), str) else ""
        if len(f"{name}:{nm}") > 64: err("skill_identity_too_long", f"{name}:{nm} (ERR:347)")
        if nm in sk_names: err("skill_identity_duplicate", f"{nm} in {sd_} and {sk_names[nm]} (ERR:348)")
        sk_names[nm] = sd_
        ay = f"skills/{sd_}/agents/openai.yaml"
        if ay in rel:
            try: y = parse_agent_yaml(read(ay).decode("utf-8"))
            except (ValueError, UnicodeDecodeError) as e: err("skill_agent_yaml_unsupported", f"{ay}: {e} (ERR:372-392)"); y = None
            if y is not None:
                for k in y:
                    if k not in ("interface", "policy", "dependencies"): err("skill_agent_dependency_unsupported", f"{ay}: only interface, policy and dependencies.tools (ERR:389-392)")
                if "interface" not in y: err("skill_agent_interface_missing", ay + " (ERR:372)")
                for k, code in (("display_name", "skill_agent_display_name_missing"), ("short_description", "skill_agent_short_description_missing")):
                    v = y.get("interface", {}).get(k)
                    if not isinstance(v, str) or not v.strip(): err(code, ay + f" interface.{k} must be a non-empty string (ERR:374-379)")
                pol = y.get("policy", {})
                if set(pol) - {"products", "allow_implicit_invocation"} or not set(pol.get("products", [])) <= {"CHAT", "CODEX"} \
                        or not isinstance(pol.get("allow_implicit_invocation", True), bool):
                    err("skill_agent_policy_invalid", ay + ": policy allows products (CHAT/CODEX) and allow_implicit_invocation (true/false) (ERR:389-391)")
                dep = y.get("dependencies", {})
                if set(dep) - {"tools"} or any(t.get("type") != "mcp" for t in dep.get("tools", [])): err("skill_agent_dependencies_wrong_type", ay + " (SKL:101-109)")
        # tool names in backticks must exist live
        for r_ in [x for x in rel if x.startswith(f"skills/{sd_}/") and x.endswith(".md")]:
            for tok in set(re.findall(r"`([a-z][a-z0-9_]*)`", read(r_).decode("utf-8"))):
                if tok in tools: continue
                if "_" in tok and tok.split("_")[0] in TOOL_VERBS:
                    err("tool_not_live", f"{r_} names tool `{tok}` which is not in the live tools list")
    return E, N, OWNER


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    submit = "--submit" in argv
    tools = TOOLS_DEFAULT
    if "--tools" in argv:
        tools = argv[argv.index("--tools") + 1]
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--tools")]
    if len(args) != 1:
        print(__doc__); return 2
    E, N, OWNER = validate(args[0], submit, tools)
    for n in N: print("note:", n)
    for o in OWNER: print("owner item:", o)
    for e in E: print("FAIL", e)
    print("RESULT:", "FAIL" if E else "OK - ready for review except owner items" if not submit else "OK - ready for review, no owner items open", f"({len(E)} errors)")
    return 1 if E else 0


if __name__ == "__main__":
    sys.exit(main())
