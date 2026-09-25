#!/usr/bin/env python3
"""
TokenViz: Visualize token usage in text prompts for OpenAI models.
"""

import os
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


@click.command()
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
@click.version_option(__version__, prog_name="tokenviz")
def main(text, file_path, model, top, threshold):
    """
    TokenViz: Visualize token usage in text prompts.

    \b
    Examples:
        tokenviz "Your prompt text here"
        tokenviz -f prompt.txt
        tokenviz -f prompt.txt --top 5
        tokenviz "Text" --model gpt-3.5-turbo
        cat prompt.txt | tokenviz
    """
    global ENCODER
    _utf8_stdout()

    # Set up encoder for specified model
    ENCODER = get_encoder(model)

    # Get input text
    if file_path:
        try:
            input_text = Path(file_path).read_text(encoding='utf-8')
        except Exception as e:
            click.secho(f"Error reading file: {e}", fg="red", err=True)
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
                click.echo(f"Enter your text ({eof} to finish):", err=True)
            input_text = sys.stdin.read()

    if not input_text.strip():
        click.secho("No input provided", fg="red", err=True)
        click.echo("Try: tokenviz \"your prompt\"  or  tokenviz -f prompt.txt  (see --help)", err=True)
        sys.exit(1)

    # Analyze the text
    total_tokens = count_tokens(input_text)
    line_analysis = analyze_lines(input_text)

    if not line_analysis:
        click.secho("No non-empty lines found", fg="yellow")
        return

    # Apply filters
    if threshold is not None:
        line_analysis = [(num, text, tokens) for num, text, tokens in line_analysis
                         if tokens > threshold]

    # Sort by token count (descending) and optionally limit
    line_analysis.sort(key=lambda x: x[2], reverse=True)

    if top:
        line_analysis = line_analysis[:top]

    # Display results
    click.secho(f"\n📊 Token Analysis (model: {model})", fg="blue", bold=True)
    click.secho(f"Total tokens: {total_tokens}", fg="green", bold=True)
    click.secho(f"Total lines analyzed: {len(line_analysis)}\n", fg="green")

    if not line_analysis:
        click.secho("No lines match the specified criteria", fg="yellow")
        return

    # Find max tokens for scaling
    max_tokens = max(tokens for _, _, tokens in line_analysis)

    # Display line breakdown
    click.secho("Line breakdown:", bold=True)
    click.secho("─" * 120, fg="cyan")

    for line_num, line_text, token_count in line_analysis:
        formatted_line = format_line_output(line_num, line_text, token_count, max_tokens)

        # Color code based on token count
        if token_count > 100:
            click.secho(formatted_line, fg="red")
        elif token_count > 50:
            click.secho(formatted_line, fg="yellow")
        else:
            click.echo(formatted_line)

    click.secho("─" * 120, fg="cyan")

    # Summary stats
    if len(line_analysis) > 1:
        shown = [tokens for _, _, tokens in line_analysis]
        avg_tokens = sum(shown) / len(shown)
        click.secho("\n📈 Stats:", fg="blue", bold=True)
        click.echo(f"  Average tokens per line: {avg_tokens:.1f}")
        click.echo(f"  Most tokens in a line:   {max(shown)}")
        click.echo(f"  Fewest tokens in a line: {min(shown)}")
        click.echo(f"  Tokens in the lines shown: {sum(shown)} of {total_tokens} total")


if __name__ == "__main__":
    main()
