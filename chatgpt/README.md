# ChatGPT directory package (WD-4138)

Builds and validates the ZIP that OpenAI's plugin directory asks for, for the "Eric's New York" plugin.
It copies the skills in `../skills/` verbatim: one skills source for every plugin. Only `agents/openai.yaml` is generated.
Python 3 standard library only.

- Build + validate: `python3 chatgpt/build.py` -> `chatgpt/dist/erics-new-york-<version>.zip` (git-ignored)
- Validate alone: `python3 chatgpt/validate.py <zip> [--submit]` (`--submit` also fails on owner-only items). A pass means "ready for review except owner items": the validator enforces the 5+3 review test cases, although upload itself accepts partial lists (SUB:649)
- Tests: `python3 -m unittest discover -s chatgpt -v`

Files: `plugin.json` and `mcp.json` (Agent Plugins format), `skill-meta.json` (feeds each skill's
`agents/openai.yaml`), `schemas/` and `tools-list.json` (reference copies the validator checks against).
`test_build.py` proves the built skills are byte-identical to `../skills/` (no patches).

Each validator rule cites OpenAI's page and line (`SUB`, `ERR`, `GUI`, `SKL` in `validate.py`).
Do not change anything outside `chatgpt/` for this package: the plugin in `../skills/` and
`../.claude-plugin/` is under separate review.
