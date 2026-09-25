# TokenViz

A small Python CLI that counts the tokens in a prompt with OpenAI's `tiktoken` and ranks its lines by token cost, with a bar chart per line so the heavy parts stand out.

When a prompt is too long or too expensive, the useful question is "which lines are doing it?". TokenViz answers that in one command: total tokens, then every non-empty line sorted by token count, with filters to show only the worst offenders.

## What it does

- Total token count for the whole input, using the tiktoken encoding for the model you name (`gpt-4` by default; unknown names fall back to the GPT-4 encoding with a warning).
- Per-line token counts, sorted highest first, each with a scaled `█` bar and a preview of the line.
- Lines over 50 tokens print in yellow, over 100 in red.
- `--top N` keeps only the N heaviest lines; `--threshold N` keeps only lines above N tokens.
- Input from an argument, a file (`-f`), or stdin.

## Install

### Download (no Python needed)

Grab a prebuilt executable from the [latest release](https://github.com/Mattbusel/tokenviz/releases/latest):

| OS | File |
| --- | --- |
| Windows | `tokenviz-vX.Y.Z-windows-x86_64.zip` |
| macOS, Apple Silicon | `tokenviz-vX.Y.Z-macos-arm64.tar.gz` |
| macOS, Intel | `tokenviz-vX.Y.Z-macos-x86_64.tar.gz` |
| Linux | `tokenviz-vX.Y.Z-linux-x86_64.tar.gz` |

Unzip it and run `tokenviz` from a terminal (`tokenviz.exe` on Windows). The tokenizer data is built in, so it works offline.

The binaries are unsigned. Windows SmartScreen may say "unknown publisher": click **More info**, then **Run anyway**. On macOS, right-click the binary and choose **Open** the first time, or run `xattr -d com.apple.quarantine tokenviz`.

### pipx

```bash
pipx install git+https://github.com/Mattbusel/tokenviz
```

Note: the name `tokenviz` on PyPI belongs to a different, unrelated package, so `pip install tokenviz` will not install this tool.

### From source

```bash
git clone https://github.com/Mattbusel/tokenviz
cd tokenviz
pip install -e ".[dev]"
pytest
```

## Usage

```bash
tokenviz "Write me a detailed story about space exploration"
tokenviz -f my_prompt.txt --top 5
tokenviz -f my_prompt.txt --threshold 20 --model gpt-3.5-turbo
cat my_prompt.txt | tokenviz
```

Without installing, `python -m tokenviz ...` does the same from the repo root.

## Layout

```
pyproject.toml            packaging, the `tokenviz` console script
tokenviz/
  __init__.py
  __main__.py             python -m tokenviz
  cli.py                  the click command: count_tokens, analyze_lines, bar rendering
tests/                    pytest suite, run by CI on Linux and Windows
```

## Related

[Token-Visualizer](https://github.com/Mattbusel/Token-Visualizer) is a sibling project by the same author: a single interactive script that also shows the individual token boundaries, supports Hugging Face tokenizers, and suggests shorter phrasings.
