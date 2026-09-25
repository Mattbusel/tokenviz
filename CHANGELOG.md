# Changelog

## [0.2.0] - 2026-09-25

- Fixed: `cli.py` and `setup.py` were truncated mid-line and raised `SyntaxError`, so nothing ran. `cli.py` is complete again (the summary stats block now prints average, max and min tokens per line) and the redundant `setup.py` is gone; `pyproject.toml` is the single source of packaging truth.
- The package now lives at the repository root, so `pipx install git+https://github.com/Mattbusel/tokenviz` installs a working `tokenviz` command.
- Prebuilt single-file executables for Windows, macOS (Apple Silicon and Intel) and Linux on every GitHub Release. They carry the tiktoken encodings, so they work offline.
- `--version`, `python -m tokenviz`, and text containing special tokens such as `<|endoftext|>` is counted instead of crashing.
- Importing the module no longer downloads an encoding.
- CI now installs the package, byte-compiles every file, runs real tests and fails when they fail (it used to swallow every error).

## [0.1.0]

- Initial version.
