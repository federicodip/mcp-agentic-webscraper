# MCP Scraper (with CLI & Report Export)

A minimal LangGraph + MCP example that can run interactively or answer a single question from the command line. This fork adds:

- CLI flags to control the model, temperature, tokens, and MCP usage
- A Markdown report exporter (`--save-report`) for transcripts/answers
- A `.env` workflow (optional) or plain environment variables

## Features

- Chat or one-shot question mode
- Optional MCP tools over `npx` (Bright Data example)
- Save responses as Markdown for later review
- Simple configuration via flags or environment variables

## Requirements

- Python 3.13+ (managed by [uv](https://github.com/astral-sh/uv) or your own Python)
- An Anthropic API key (`ANTHROPIC_API_KEY`)
- Optional MCP server via `npx` if you want tools
- Windows PowerShell examples below; adapt as needed for other shells

## Quick Start

```powershell
# Install dependencies (recommended with uv)
uv sync

# Verify you have an Anthropic key in the environment
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# One-shot question + save a Markdown report
uv run main.py --question "What is theguardian.com about?" --save-report reports/guardian.md
```

## Installation

```powershell
# From the project folder
uv sync
```

If you prefer a virtualenv without uv:
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e .
```

## Configuration

You can configure credentials either via environment variables or a `.env` file. The code calls `load_dotenv()` so a local `.env` will be loaded automatically if present.

### Required

- `ANTHROPIC_API_KEY` – your Anthropic key

### Optional (only if using MCP tools)

- `API_TOKEN`
- `BROWSER_AUTH` (e.g., `persist`)
- `WEB_UNLOCKER_ZONE`

#### Set variables in PowerShell (temporary for this terminal)

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:API_TOKEN = "<optional>"
$env:BROWSER_AUTH = "persist"
$env:WEB_UNLOCKER_ZONE = "<optional>"
```

#### Or use a `.env` file (kept out of git)

```
ANTHROPIC_API_KEY=sk-ant-...
API_TOKEN=
BROWSER_AUTH=persist
WEB_UNLOCKER_ZONE=
```

Ensure `.env` is listed in `.gitignore`.

## Usage

### Interactive chat

```powershell
uv run main.py
# then type your messages; 'exit' or 'quit' to stop
```

Save each response to a single Markdown file while chatting:
```powershell
uv run main.py --save-report reports/session.md
```

### One-shot question

```powershell
uv run main.py --question "What is repubblica.it about?"
```

One-shot plus report export:
```powershell
uv run main.py --question "What is theguardian.com about?" --save-report reports/guardian.md
```

### Disable MCP tools

If you haven’t configured MCP or just want the LLM:

```powershell
uv run main.py --no-mcp --question "hello"
```

### Choose model and tuning

```powershell
uv run main.py --model claude-4-sonnet-20250514 --temperature 0.2 --max-tokens 1024 --question "Summarize..."
```

## Project Structure

```
.
├─ main.py            # CLI, chat loop, agent wiring, report export hook
├─ reporting.py       # write_markdown_report(messages, ai_reply, out_path, meta)
├─ pyproject.toml     # project metadata and deps
├─ README.md
└─ .env               # optional, not committed
```

## Troubleshooting

- **Nothing saves when I type `--save-report` in the chat.**  
  Flags belong on the command line, not inside the chat. Start with:
  ```powershell
  uv run main.py --save-report reports/session.md
  ```
  Then type only your question in the chat.

- **`Missing ANTHROPIC_API_KEY`**  
  Set it before running:
  ```powershell
  $env:ANTHROPIC_API_KEY = "sk-ant-..."
  ```

- **MCP “technical difficulties”**  
  Either disable MCP:
  ```powershell
  uv run main.py --no-mcp --question "..."
  ```
  Or set the MCP variables as shown in Configuration.

- **Model not found (404)**  
  Use a current model id (default here: `claude-4-sonnet-20250514`). If you still see 404, list models available to your account and pick from those.

- **`ModuleNotFoundError: reporting`**  
  Ensure `reporting.py` is in the same folder as `main.py`.

- **`npx` not found**  
  Install Node.js or use `--no-mcp`.

## How to Publish to GitHub

1. Create a new repo on GitHub (no files).
2. In your project folder:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit: CLI flags + report export"
   git branch -M main
   git remote add origin https://github.com/<you>/<repo>.git
   git push -u origin main
   ```
3. If prompted, authenticate with your browser or a personal access token.

## License & Attribution

If this began from another repository, keep that project’s license and attribution, and ensure your license is compatible. Do not commit secrets (API keys) to the repository.

## Roadmap

- Optional logging to JSON/CSV
- Basic unit test for `write_markdown_report`
- GitHub Actions workflow for linting/tests
