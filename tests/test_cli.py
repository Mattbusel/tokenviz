"""Tests for the tokenviz CLI. The first run downloads tiktoken's GPT-4 encoding."""
from click.testing import CliRunner

from tokenviz import __version__
from tokenviz.cli import analyze_lines, count_tokens, create_token_bar, main


def test_count_tokens():
    assert count_tokens("hello world") == 2
    # Special-token text in a prompt is counted, not rejected.
    assert count_tokens("<|endoftext|>") > 0


def test_analyze_lines_skips_blank_lines():
    rows = analyze_lines("one two\n\n   \nthree")
    assert [(n, t) for n, t, _ in rows] == [(1, "one two"), (4, "three")]


def test_create_token_bar_scales():
    assert create_token_bar(10) == "█" * 10
    assert len(create_token_bar(200, max_tokens=200)) == 50
    assert len(create_token_bar(100, max_tokens=200)) == 25


def test_version():
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_text_argument_and_stats():
    prompt = "short line\n" + "a much longer line with quite a few more words in it than the first\n"
    result = CliRunner().invoke(main, [prompt])
    assert result.exit_code == 0, result.output
    assert "Total tokens:" in result.output
    assert "Stats:" in result.output
    assert "Average tokens per line:" in result.output


def test_file_top_and_threshold(tmp_path):
    path = tmp_path / "prompt.txt"
    path.write_text("a\nb c d e f g h i j k l m n o p\nq r s\n", encoding="utf-8")
    result = CliRunner().invoke(main, ["-f", str(path), "--top", "1"])
    assert result.exit_code == 0, result.output
    assert "Total lines analyzed: 1" in result.output
    assert "b c d" in result.output
    result = CliRunner().invoke(main, ["-f", str(path), "--threshold", "100"])
    assert "No lines match" in result.output


def test_stdin_and_unknown_model():
    result = CliRunner().invoke(main, ["--model", "not-a-model"], input="hello there\n")
    assert result.exit_code == 0, result.output
    assert "Total tokens: 3" in result.output  # "hello there" plus the newline
    assert "Unknown model" in result.output


def test_empty_input_fails():
    result = CliRunner().invoke(main, [], input="   \n")
    assert result.exit_code == 1


def test_budget_exit_codes():
    ok = CliRunner().invoke(main, ["hello world", "--budget", "5"])
    assert ok.exit_code == 0, ok.output
    assert "Within budget: 2 of 5 tokens" in ok.output
    over = CliRunner().invoke(main, ["hello world", "--budget", "1"])
    assert over.exit_code == 3
    assert "Over budget: 2 tokens > 1" in over.output


def test_json_output():
    import json

    result = CliRunner().invoke(main, ["one\ntwo three four five", "--json", "--top", "1"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["encoding"] == "cl100k_base"
    assert data["lines_total"] == 2
    assert [row["line"] for row in data["lines"]] == [2]
    assert data["over_budget"] is False


def test_no_color_and_force_color(monkeypatch):
    monkeypatch.setenv("FORCE_COLOR", "1")
    colored = CliRunner().invoke(main, ["hello world"])
    assert "\x1b[" in colored.output
    plain = CliRunner().invoke(main, ["hello world", "--no-color"])
    assert "\x1b[" not in plain.output
    monkeypatch.setenv("NO_COLOR", "1")
    assert "\x1b[" not in CliRunner().invoke(main, ["hello world"]).output
