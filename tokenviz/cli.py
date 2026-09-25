#!/usr/bin/env python3
"""
TokenViz: count the tokens in a prompt and rank its lines by token cost.
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import click
import tiktoken

from . import __version__

DEFAULT_MODEL = "gpt-4"


def _use_bundled_encodings() -> None:
    """Point tiktoken at the encodings shipped inside a PyInstaller build.

    tiktoken normally downloads its encoding files on first use. The prebuilt
    executables carry them, so they work offline; a user-set
    TIKTOKEN_CACHE_DIR always wins.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base and "TIKTOKEN_CACHE_DIR" not in os.environ:
        cache = os.path.join(base, "tiktoken_cache")
        if os.path.isdir(cache):
            os.environ["TIKTOKEN_CACHE_DIR"] = cache


_use_bundled_encodings()

# Loaded on first use, so importing the module never touches the network.
ENCODER: Optional["tiktoken.Encoding"] = None


def get_encoder(model: str = DEFAULT_MODEL) -> "tiktoken.Encoding":
    """Return the tiktoken encoding for ``model``, falling back to GPT-4's."""
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        click.secho(f"Warning: Unknown model '{model}', using {DEFAULT_MODEL} encoding",
                    fg="yellow", err=True)
        return tiktoken.encoding_for_model(DEFAULT_MODEL)


def count_tokens(text: str) -> int:
    """Count tokens in text using OpenAI's tiktoken."""
    global ENCODER
    if ENCODER is None:
        ENCODER = get_encoder(DEFAULT_MODEL)
    return len(ENCODER.encode(text, disallowed_special=()))


def analyze_lines(text: str) -> List[Tuple[int, str, int]]:
    """Analyze text and return (line_num, line_text, token_count) tuples."""
    results = []
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip():  # Skip empty lines
            results.append((i, line, count_tokens(line)))
    return results


def create_token_bar(token_count: int, max_width: int = 50, max_tokens: Optional[int] = None) -> str:
    """Create a visual bar representing token count."""
    if max_tokens is None:
        max_tokens = max_width

    # Scale the bar based on token count
    bar_length = min(token_count, max_width)
    if max_tokens > max_width:
        bar_length = int((token_count / max_tokens) * max_width)

    return "█" * bar_length


def format_line_output(line_num: int, line_text: str, token_count: int, max_tokens: int) -> str:
    """Format a single line's output with visual bar."""
    bar = create_token_bar(token_count, max_tokens=max_tokens)
    truncated_line = line_text.strip()

    # Truncate long lines for display
    if len(truncated_line) > 80:
        truncated_line = truncated_line[:77] + "..."

    return f"{line_num:>3}: {token_count:>3} tokens | {bar:<50} | {truncated_line}"


def _utf8_stdout() -> None:
    """Pipes on Windows default to a legacy code page that cannot print the bars."""
    for stream in (sys.stdout, sys.stderr):
        encoding = (getattr(stream, "encoding", "") or "").lower().replace("-", "")
        if encoding != "utf8":
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError):
                pass


def _color_choice(no_color: bool) -> Optional[bool]:
    """False for --no-color or NO_COLOR, True for FORCE_COLOR, else auto (terminal only)."""
    if no_color or os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return None


def _layout(width: int) -> Tuple[int, int]:
    """Bar width and line-preview width that fit a terminal `width` columns wide."""
    fixed = 5 + 11 + 3 + 3 + 7 + 3  # "123: " "1234 tokens" " | " " | " " 12.3%" " | "
    room = max(40, width - fixed)
    bar = max(10, min(24, room // 4))
    return bar, max(20, room - bar)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("text", required=False)
@click.option("--file", "-f", "file_path",
              type=click.Path(exists=True, dir_okay=False),
              help="Read input from a file")
@click.option("--model", "-m",
              default=DEFAULT_MODEL, show_default=True,
              help="Model to use for tokenization (gpt-4, gpt-4o, gpt-3.5-turbo, etc.)")
@click.option("--top", "-t",
              type=click.IntRange(min=1),
              help="Show only the top N lines with most tokens")
@click.option("--threshold",
              type=click.IntRange(min=0),
              help="Only show lines with more than N tokens")
@click.option("--budget", "-b",
              type=click.IntRange(min=1),
              help="Exit with code 3 if the whole input is over N tokens (for CI and scripts)")
@click.option("--json", "as_json", is_flag=True,
              help="Print machine-readable JSON instead of the chart")
@click.option("--no-color", is_flag=True, help="Disable colors (NO_COLOR is also respected)")
@click.version_option(__version__, "-V", "--version", prog_name="tokenviz")
def main(text, file_path, model, top, threshold, budget, as_json, no_color):
    """
    Count the tokens in a prompt and rank its lines by token cost.

    \b
    Examples:
        tokenviz "Your prompt text here"
        tokenviz -f prompt.txt --top 5          the 5 heaviest lines
        tokenviz -f prompt.txt --threshold 20   only lines over 20 tokens
        tokenviz -f prompt.txt -m gpt-4o        GPT-4o's tokenizer (o200k_base)
        cat prompt.txt | tokenviz
        tokenviz -f prompt.txt --budget 2000    exit 3 if over 2000 tokens
        tokenviz -f prompt.txt --json           JSON for scripts
    """
    global ENCODER
    _utf8_stdout()
    color = _color_choice(no_color)

    def say(message="", err=False, **style):
        click.secho(message, err=err, color=color, **style)

    # Set up encoder for specified model
    ENCODER = get_encoder(model)

    # Get input text
    if file_path:
        try:
            input_text = Path(file_path).read_text(encoding='utf-8')
        except Exception as e:
            say(f"Error reading file: {e}", err=True, fg="red")
            sys.exit(1)
    elif text:
        input_text = text
    else:
        # Read from stdin
        if sys.stdin is None:
            input_text = ""
        else:
            if sys.stdin.isatty():
                eof = "Ctrl+Z then Enter" if os.name == "nt" else "Ctrl+D"
                say(f"Paste or type your prompt, then press {eof} on a new line:", err=True)
            input_text = sys.stdin.read()

    if not input_text.strip():
        say("No input provided", err=True, fg="red")
        say("Try: tokenviz \"your prompt\"  or  tokenviz -f prompt.txt  (see --help)", err=True)
        sys.exit(1)

    # Analyze the text
    total_tokens = count_tokens(input_text)
    all_lines = analyze_lines(input_text)
    line_analysis = list(all_lines)

    # Apply filters
    if threshold is not None:
        line_analysis = [(num, text, tokens) for num, text, tokens in line_analysis
                         if tokens > threshold]

    # Sort by token count (descending) and optionally limit
    line_analysis.sort(key=lambda x: x[2], reverse=True)

    if top:
        line_analysis = line_analysis[:top]

    over_budget = budget is not None and total_tokens > budget

    if as_json:
        click.echo(json.dumps({
            "model": model,
            "encoding": ENCODER.name,
            "total_tokens": total_tokens,
            "lines_total": len(all_lines),
            "budget": budget,
            "over_budget": over_budget,
            "lines": [{"line": n, "tokens": t, "text": s} for n, s, t in line_analysis],
        }, indent=2, ensure_ascii=False))
        sys.exit(3 if over_budget else 0)

    width = shutil.get_terminal_size((100, 24)).columns
    bar_width, preview_width = _layout(width)
    rule = "─" * min(width, bar_width + preview_width + 32)

    say()
    say("Token Analysis", bold=True, fg="blue", nl=False)
    say(f"  model {model}, encoding {ENCODER.name}", dim=True)
    say("Total tokens: ", nl=False)
    say(f"{total_tokens}", fg="green", bold=True, nl=False)
    say(f"   across {len(all_lines)} non-empty lines", dim=True)
    say(f"Total lines analyzed: {len(line_analysis)}")
    say()

    if not all_lines:
        say("No non-empty lines found", fg="yellow")
        return

    if not line_analysis:
        say("No lines match the specified criteria", fg="yellow")
    else:
        # Find max tokens for scaling
        max_tokens = max(tokens for _, _, tokens in line_analysis)

        say("Line breakdown", bold=True, nl=False)
        say("  heaviest first; yellow > 50 tokens, red > 100", dim=True)
        say(rule, fg="cyan", dim=True)

        for line_num, line_text, token_count in line_analysis:
            # The heaviest line gets the full bar; the rest are to scale.
            bar = "█" * max(1, round(token_count / max_tokens * bar_width))
            share = 100.0 * token_count / total_tokens if total_tokens else 0.0
            preview = line_text.strip()
            if len(preview) > preview_width:
                preview = preview[:preview_width - 3] + "..."
            fg = "red" if token_count > 100 else "yellow" if token_count > 50 else None
            say(f"{line_num:>3}: {token_count:>4} tokens ", fg=fg, bold=fg is not None, nl=False)
            say("| ", dim=True, nl=False)
            say(f"{bar:<{bar_width}}", fg=fg or "cyan", nl=False)
            say(f" | {share:5.1f}% | ", dim=True, nl=False)
            say(preview)

        say(rule, fg="cyan", dim=True)

        # Summary stats
        if len(line_analysis) > 1:
            shown = [tokens for _, _, tokens in line_analysis]
            avg_tokens = sum(shown) / len(shown)
            say()
            say("Stats:", fg="blue", bold=True)
            say(f"  Average tokens per line: {avg_tokens:.1f}")
            say(f"  Most tokens in a line:   {max(shown)}")
            say(f"  Fewest tokens in a line: {min(shown)}")
            say(f"  Tokens in the lines shown: {sum(shown)} of {total_tokens} total")

    if budget is not None:
        say()
        if over_budget:
            say(f"Over budget: {total_tokens} tokens > {budget} (exit code 3)", fg="red", bold=True)
            sys.exit(3)
        say(f"Within budget: {total_tokens} of {budget} tokens", fg="green", bold=True)


if __name__ == "__main__":
    main()
