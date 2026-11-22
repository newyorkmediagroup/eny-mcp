# ChatGPT directory package (WD-4138)

Builds and validates the ZIP that OpenAI's plugin directory asks for, for the "Eric's New York" plugin.
It copies the skills in `../skills/` (one skills source for every plugin), applying only the listed edits. Only `agents/openai.yaml` is generated.
Python 3 standard library only.

- Build + validate: `python3 chatgpt/build.py` -> `chatgpt/dist/erics-new-york-<version>.zip` (git-ignored)
- Validate alone: `python3 chatgpt/validate.py <zip> [--submit]` (`--submit` also fails on owner-only items). A pass means "ready for review except owner items": the validator enforces the 5+3 review test cases, although upload itself accepts partial lists (SUB:649)
- Tests: `python3 -m unittest discover -s chatgpt -v`

Files: `plugin.json` and `mcp.json` (Agent Plugins format), `skill-meta.json` (feeds each skill's
`agents/openai.yaml`), `schemas/` and `tools-list.json` (reference copies the validator checks against).
The `walking-routes-in-the-app` skill is not shipped to ChatGPT (`NOT_SHIPPED` in `build.py`): walking routes are a paid digital product in the app, and the directory allows commerce for physical goods only. Shared skills are copied verbatim except the text edits listed in `skill-edits.json` (each `old` must match exactly once, else the build stops): the ChatGPT directory package carries no walking routes and no unprompted social or newsletter invitation. `test_build.py` proves everything else is byte-identical to `../skills/`.

Each validator rule cites OpenAI's page and line (`SUB`, `ERR`, `GUI`, `SKL` in `validate.py`).
Package metadata and build code live in `chatgpt/`. All shared skill content is edited only in `../skills/`
(never copied here), and `../.claude-plugin/` is not part of this package.
