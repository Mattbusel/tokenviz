import click
import tiktoken
import sys
from pathlib import Path
from typing import List, Tuple

# Default to GPT-4 encoding
ENCODER = tiktoken.encoding_for_model("gpt-4")

def count_tokens(text: str) -> int:
    """Count tokens in text using OpenAI's tiktoken."""
    return len(ENCODER.encode(text))

def analyze_lines(text: str) -> List[Tuple[int, str, int]]:
    """Analyze text and return (line_num, line_text, token_count) tuples."""
    lines = text.splitlines()
    results = []
    
    for i, line in enumerate(lines, 1):
        if line.strip():  # Skip empty lines
            token_count = count_tokens(line)
            results.append((i, line, token_count))
    
    return results

def create_token_bar(token_count: int, max_width: int = 50, max_tokens: int = None) -> str:
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

@click.command()
@click.argument("text", required=False)
@click.option("--file", "-f", "file_path", 
              type=click.Path(exists=True), 
              help="Read input from a file")
@click.option("--model", "-m", 
              default="gpt-4", 
              help="Model to use for tokenization (gpt-4, gpt-3.5-turbo, etc.)")
@click.option("--top", "-t", 
              type=int, 
              help="Show only the top N lines with most tokens")
@click.option("--threshold", 
              type=int, 
              help="Only show lines with more than N tokens")
def main(text, file_path, model, top, threshold):
    """
    TokenViz: Visualize token usage in text prompts.
    
    Examples:
        tokenviz "Your prompt text here"
        tokenviz -f prompt.txt
        tokenviz -f prompt.txt --top 5
        tokenviz "Text" --model gpt-3.5-turbo
    """
    global ENCODER
    
    # Set up encoder for specified model
    try:
        ENCODER = tiktoken.encoding_for_model(model)
    except KeyError:
        click.secho(f"Warning: Unknown model '{model}', using gpt-4 encoding", 
                   fg="yellow", err=True)
        ENCODER = tiktoken.encoding_for_model("gpt-4")
    
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
        if sys.stdin.isatty():
            click.echo("Enter your text (Ctrl+D to finish):")
        input_text = sys.stdin.read()
    
    if not input_text.strip():
        click.secho("No input provided", fg="red", err=True)
        sys.exit(1)
    
    # Analyze the text
    total_tokens = count_tokens(input_text)
    line_analysis = analyze_lines(input_text)
    
    if not line_analysis:
        click.secho("No non-empty lines found", fg="yellow")
        return
    
    # Apply filters
    if threshold:
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
        avg_tokens = sum(tokens for _, _, tokens in line_analysis) / len(line_analysis)
        click.secho(f"\n📈 Stats:", fg="blue", bold=True)
        click.secho(f"Average tokens per line: {avg_tokens:.1f}")
        click.secho(f"Highest token line: {max_tokens} tokens")
        click.secho(f"Lines over 50 tokens: {sum(1 for _, _, t in line_analysis if t > 50)}")

if __name__ == "__main__":
    main()