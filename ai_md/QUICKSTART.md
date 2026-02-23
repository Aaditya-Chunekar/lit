# Quick Start Guide for `lit`

## Installation

### 1. Clone and Install

```bash
cd ~/Program/opensource/lit
pip install -e .
```

### 2. Set Up Lingo API Key

```bash
export LINGODOTDEV_API_KEY="your-api-key-from-lingo.dev"
```

You can also add this to your `.bashrc`, `.zshrc`, or Windows environment variables.

### 3. Verify Installation

```bash
lit --help
```

You should see:

```
 Usage: lit [OPTIONS] COMMAND [ARGS]...

 Type how you think, commit effortlessly. Git wrapper with AI-powered commits.

 Options:
   --help  Show this message and exit.
```

## Testing the CLI

### Test 1: Git Passthrough Commands

```bash
# Create a test repo if you don't have one
mkdir test-repo
cd test-repo
git init

# Test basic git commands
lit status                    # Should show "On branch main"
lit log                       # Should work (empty initially)
git add README.md            # Pre-stage a file
lit status                   # Should show staged changes
```

### Test 2: Commit Flow (Without API Key)

If you don't have a Lingo API key yet, the fallback heuristic will kick in:

```bash
# Stage a file
echo "# Test" > README.md
git add README.md

# Run lit commit with a message
lit commit -m "add README documentation"
```

You should see:
- Loading spinner
- Warning about API key
- Fallback commit generation
- Preview of the commit
- Confirmation prompt

### Test 3: With API Key

Once you set `LINGODOTDEV_API_KEY`:

```bash
# Test with English message
lit commit -m "fix: correct login validation"

# Test with mixed language
lit commit -m "login ka bug fix kiya"

# Test with Hindi-English mix
lit commit -m "database migration kiya aur models update kiye"
```

## Project Structure

```
lit/
├── __main__.py           # Entrypoint (calls cli.app())
├── __init__.py           # Package metadata
├── cli.py                # Typer router (commit vs git passthrough)
├── git_utils.py          # Git subprocess operations
├── lingo_utils.py        # Lingo SDK integration + JSON parsing
├── commit_flow.py        # Full commit orchestration (validation → translation → confirmation)
├── pyproject.toml        # Dependencies and metadata
├── README.md             # Full documentation
├── QUICKSTART.md         # This file
└── .gitignore            # Git ignore rules
```

## Code Walkthrough

### Entry Point: `__main__.py`

```python
def main() -> None:
    app()  # Typer app from cli.py
```

### Router: `cli.py`

```python
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if args[0] == "commit":
        _handle_commit(args)  # Special flow
    else:
        passthrough_git_command()  # Regular git
```

### Commit Flow: `commit_flow.py`

```python
async def run_commit_flow(raw_message: str) -> bool:
    1. is_git_repo()
    2. get_staged_files()
    3. get_staged_diff()
    4. translate_commit_message(message, diff)  # Async Lingo SDK
    5. show_preview()
    6. ask_confirmation()  # questionary
    7. commit_with_message()
```

### Translation: `lingo_utils.py`

```python
async def translate_commit_message(raw_message, staged_diff):
    # Call Lingo SDK with system instruction
    async with LingoDotDevEngine(...) as engine:
        result = await engine.localize_object(
            {
                "instruction": "...",
                "raw_message": raw_message,
                "diff": staged_diff
            },
            {"source_locale": None, "target_locale": "en", "fast": False}
        )
    
    # Parse JSON response
    commit = parse_lingo_response(result)
    
    # Fallback if parsing fails
    if not commit:
        commit = fallback_generate_commit(raw_message, diff)
    
    return commit
```

## Edge Cases Handled

✅ Missing LINGODOTDEV_API_KEY
- Shows helpful error, suggests setting env var
- Can still test with fallback

✅ No staged files
- Shows "No staged files. Run git add first."

✅ Invalid JSON from SDK
- Falls back to heuristic generation
- Uses keywords: fix, feat, chore, refactor

✅ Network/SDK errors
- Catches RuntimeError, ValueError
- Gracefully falls back
- Shows warning but continues

✅ git not installed
- Catches FileNotFoundError
- Shows helpful message

✅ User keyboard interrupt
- Handles Ctrl+C gracefully
- "Interrupted by user."

## Production Checklist

- [x] All git commands pass through directly
- [x] Async SDK integration with proper event loop
- [x] Fallback heuristics if SDK fails
- [x] Clean, modular code
- [x] Rich terminal output (colors, spinner, panels)
- [x] Interactive confirmation (questionary)
- [x] Error handling for all edge cases
- [x] Type hints throughout
- [x] Docstrings for all functions
- [x] Conventional Commit validation
- [x] Support for mixed languages
- [x] JSON parsing with strict validation
- [x] Async context manager properly closed
- [x] Exit codes returned correctly
- [x] No unnecessary abstractions

## What Makes This Hackathon-Ready

1. **Live Demo**: Works immediately out of the box
2. **Polished UX**: Rich spinners, colored output, interactive prompts
3. **Fallback Magic**: Works even without API key (heuristic generation)
4. **Production Code**: Proper error handling, type hints, docstrings
5. **Modular Design**: Each component is testable and reusable
6. **Git-Native**: Zero friction for users, behaves like git
7. **Smart Translation**: Handles mixed languages (Hinglish, etc.)
8. **Premium Feel**: Feels like a real product, not a weekend hack

## Next Steps

1. Get Lingo API key from https://lingo.dev
2. Set `LINGODOTDEV_API_KEY` environment variable
3. Test with various commit messages
4. Try mixed language commits (Hinglish, etc.)
5. Customize the prompts/output if needed

## Demo Script

```bash
#!/bin/bash

# Setup
mkdir demo-repo && cd demo-repo
git init

# Add initial file
echo "# My Project" > README.md
git add README.md

# Test commit with Hinglish
lit commit -m "initial setup kiya aur README add kiya"

# Make another change
echo "## Features" >> README.md
git add README.md

# Test commit with English
lit commit -m "add features section"

# Make a breaking change
echo "BREAKING CHANGE: Removed legacy API" > BREAKING.md
git add BREAKING.md

# Test commit with mixed message
lit commit -m "legacy API remove kiya"

# View the log
lit log --oneline
```

Enjoy building with `lit`! 🔥
