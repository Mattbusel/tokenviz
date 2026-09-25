# TokenViz

A small Python CLI that counts the tokens in a prompt with OpenAI's `tiktoken` and ranks its lines by token cost, with a bar chart per line so the heavy parts stand out.

When a prompt is too long or too expensive, the useful question is "which lines are doing it?". TokenViz answers that in one command: total tokens, then every non-empty line sorted by token count, with filters to show only the worst offenders.

## What it does

- Total token count for the whole input, using the tiktoken encoding for the model you name (`gpt-4` by default; unknown names fall back to the GPT-4 encoding with a warning).
- Per-line token counts, sorted highest first, each with a scaled `█` bar and a preview of the line.
- Lines over 50 tokens print in yellow, over 100 in red.
- `--top N` keeps only the N heaviest lines; `--threshold N` keeps only lines above N tokens.
- Input from an argument, a file (`-f`), or stdin.

## Quick start

```bash
git clone https://github.com/Mattbusel/tokenviz
cd tokenviz/tokenviz
pip install -r requirements.txt     # tiktoken, click

python -m tokenviz.cli "Write me a detailed story about space exploration"
python -m tokenviz.cli -f my_prompt.txt --top 5
python -m tokenviz.cli -f my_prompt.txt --threshold 20 --model gpt-3.5-turbo
cat my_prompt.txt | python -m tokenviz.cli
```

Note: the name `tokenviz` on PyPI belongs to a different, unrelated package, so `pip install tokenviz` will not install this tool. Install from source.

## Layout

```
tokenviz/                 package root (pyproject.toml, setup.py, requirements.txt)
  tokenviz/
    __init__.py
    cli.py                the click command: count_tokens, analyze_lines, bar rendering
```

`setup.py` declares a `tokenviz` console script pointing at `tokenviz.cli:main`.

## Status

Early and currently broken as committed. The last lines of `tokenviz/tokenviz/cli.py` (the summary stats block) and of `tokenviz/setup.py` are cut off mid-statement, so both files raise a `SyntaxError` and the commands above fail until those files are completed. The CI workflow installs dependencies and runs pytest if tests exist; there are no tests yet, so a green run does not mean the tool works.

## Related

[Token-Visualizer](https://github.com/Mattbusel/Token-Visualizer) is a sibling project by the same author: a single interactive script that also shows the individual token boundaries, supports Hugging Face tokenizers, and suggests shorter phrasings.
