 TokenViz - Visualize Token Usage in Your Prompts

A fast, clean CLI tool to analyze token usage in text prompts for OpenAI models. Perfect for prompt engineering, staying under token limits, and optimizing your AI interactions.

##  Quick Start

```bash
# Install
pip install tokenviz

# Analyze a prompt
tokenviz "Write me a detailed story about space exploration"

# Analyze a file
tokenviz -f my_prompt.txt

# Show only the top 5 most token-heavy lines
tokenviz -f large_prompt.txt --top 5
 Features

 Token counting - Accurate token counts using OpenAI's tiktoken
 Line-by-line analysis - See exactly which lines use the most tokens
 Visual bars - Instant visual feedback with colorful token bars
 Smart filtering - Focus on high-token lines with --top and --threshold
 Model support - Works with GPT-4, GPT-3.5-turbo, and other OpenAI models
 Flexible input - Text, files, or stdin

 Usage
Basic Usage
bash# Direct text input
tokenviz "Your prompt text here"

# From a file
tokenviz -f prompt.txt

# From stdin
echo "Your prompt" | tokenviz
Advanced Options
bash# Use a specific model for tokenization
tokenviz -f prompt.txt --model gpt-3.5-turbo

# Show only top 10 lines with most tokens
tokenviz -f prompt.txt --top 10

# Show only lines with more than 20 tokens
tokenviz -f prompt.txt --threshold 20

# Combine filters
tokenviz -f prompt.txt --top 5 --threshold 15
 Example Output
 Token Analysis (model: gpt-4)
Total tokens: 127
Total lines analyzed: 8

Line breakdown:
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  3:  45 tokens | ████████████████████████████████████████████████ | You are an expert software engineer with deep knowledge of Python...
  1:  28 tokens | ██████████████████████████████████                | Write a comprehensive guide for building REST APIs with FastAPI
  5:  22 tokens | ████████████████████████████                      | Include examples of authentication and database integration
  7:  18 tokens | ████████████████████████                          | Make sure to cover testing best practices
  8:  14 tokens | ████████████████                                  | The guide should be beginner-friendly
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

 Stats:
Average tokens per line: 25.4
Highest token line: 45 tokens
Lines over 50 tokens: 0
🛠 Installation
From PyPI (Recommended)
bashpip install tokenviz
From Source
bashgit clone https://github.com/Mattbusel/tokenviz


cd tokenviz
pip install -e .
 Use Cases

Prompt Engineering - Optimize your prompts to stay under token limits
Cost Optimization - Identify token-heavy sections to reduce API costs
Debugging - Understand why your prompt is hitting token limits
Content Analysis - Analyze documents for token distribution
Batch Processing - Process multiple files to find token patterns

 Supported Models
TokenViz supports all OpenAI models that tiktoken supports:

gpt-4 (default)
gpt-3.5-turbo
text-davinci-003
text-curie-001
And more...

 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
 License
MIT License - see LICENSE file for details.
 Why TokenViz?
Token limits are one of the biggest pain points when working with AI models. TokenViz makes it dead simple to:

See exactly where your tokens are going
Optimize your prompts visually
Stay under limits without guesswork
Debug token issues instantly

No more counting tokens manually or hitting mysterious limits. Just clean, visual token analysis in seconds.

⭐ Star this repo if TokenViz helps you optimize your prompts!
