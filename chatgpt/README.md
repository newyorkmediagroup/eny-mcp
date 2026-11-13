# ChatGPT directory package (WD-4138)

Builds and validates the ZIP that OpenAI's plugin directory asks for, for the "Eric's New York" plugin.
It reuses the skills in `../skills/` without editing them, plus one ChatGPT-only skill (`skills/omny-card`).
Python 3 standard library only.

- Build + validate: `python3 chatgpt/build.py` -> `chatgpt/dist/erics-new-york-<version>.zip` (git-ignored)
- Validate alone: `python3 chatgpt/validate.py <zip> [--submit]` (`--submit` also fails on owner-only items). A pass means "ready for review except owner items": the validator enforces the 5+3 review test cases, although upload itself accepts partial lists (SUB:649)
- Tests: `python3 -m unittest chatgpt/test_validate.py -v`

Files: `plugin.json` and `mcp.json` (Agent Plugins format), `skill-meta.json` (feeds each skill's
`agents/openai.yaml`), `schemas/` and `tools-list.json` (reference copies the validator checks against).
`build.py` patches shared skill text in the build copy only; each patch must match exactly once.

Each validator rule cites OpenAI's page and line (`SUB`, `ERR`, `GUI`, `SKL` in `validate.py`).
Do not change anything outside `chatgpt/` for this package: the plugin in `../skills/` and
`../.claude-plugin/` is under separate review.
