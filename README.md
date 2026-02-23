# lit 🔥

**Type how you think, commit effortlessly.**

A production-ready Python CLI tool that wraps `git` and intelligently generates **Conventional Commits** using AI translation and diff analysis.

## Features

✨ **Intelligent Commit Generation**
- Detects and translates mixed languages (e.g., Hinglish, Hindi + English)
- Analyzes git diffs to understand changes
- Generates properly formatted Conventional Commits
- Interactive preview and confirmation

🎯 **Pure Git Passthrough**
- All non-commit commands behave exactly like `git`
- No friction, no surprises
- Full git compatibility

🚀 **Production-Ready**
- Async SDK integration with proper error handling
- Fallback heuristics if translation fails
- Clean, premium CLI UX with rich output
- Modular, testable codebase

## Installation

```bash
pip install lit-cli
```

Or from source:

```bash
git clone https://github.com/yourusername/lit.git
cd lit
pip install -e .
```

## Setup

Set your Lingo.dev API key:

```bash
export LINGODOTDEV_API_KEY="your-api-key-here"
```

## Usage

### Git Commands (Passthrough)

All standard git commands work exactly as expected:

```bash
lit status                          # → git status
lit add file.py                     # → git add file.py
lit log --oneline                   # → git log --oneline
lit checkout -b feature-branch      # → git checkout -b feature-branch
lit push -u origin main             # → git push -u origin main
lit merge develop                   # → git merge develop
```

### Commit with AI Translation

The **only** special command is `lit commit`:

```bash
lit commit -m "login ka bug fix kiya aur validation add kiya"
```

**What happens:**

1. ✅ **Validation**: Checks if files are staged
2. 🔄 **Translation**: Detects Hinglish, translates to English
3. 📊 **Analysis**: Examines the git diff
4. 🤖 **Generation**: Creates a Conventional Commit via Lingo.dev
5. 👀 **Preview**: Shows you the formatted commit
6. ⚡ **Confirmation**: Ask accept, edit, or cancel

```
┌──────────────────────────────────────────┐
│         Commit Preview                   │
├──────────────────────────────────────────┤
│ fix: add validation checks to login      │
│                                          │
│ - detect missing required fields         │
│ - resolve null pointer issue             │
│ - improve error messages                 │
└──────────────────────────────────────────┘

Commit with this message?
→ ✓ Accept
  ✏ Edit manually
  ✗ Cancel
```

## Conventional Commit Format

Generated commits follow the standard format:

```
<type>(<optional scope>): <description>

<body explaining what and why>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `refactor`: Code refactoring
- `docs`: Documentation changes
- `chore`: Build, CI, dependencies
- `test`: Adding tests
- `perf`: Performance improvements

**Example:**

```
fix: correct login validation logic

- add required field checks
- resolve null pointer issue
- improve error message clarity
```

## Architecture

```
lit/
├── __main__.py        # Entry point
├── cli.py             # Typer router
├── git_utils.py       # Git subprocess wrappers
├── lingo_utils.py     # Lingo SDK integration
├── commit_flow.py     # Commit orchestration
└── __init__.py        # Package exports
```

### Module Responsibilities

- **cli.py**: Routes commands → commit flow or git passthrough
- **git_utils.py**: Subprocess wrappers for git operations
- **lingo_utils.py**: Async Lingo.dev SDK integration + JSON parsing
- **commit_flow.py**: Orchestrates the full commit workflow
- **__main__.py**: CLI entrypoint

## Error Handling

The tool gracefully handles:

❌ **Missing LINGODOTDEV_API_KEY**
→ Clear error message with setup instructions

❌ **No Staged Files**
→ Helpful message: "Run `git add` first"

❌ **Invalid JSON from SDK**
→ Fallback heuristic generation

❌ **Network/SDK Errors**
→ Automatic fallback to keyword-based commit generation

❌ **Git Errors**
→ Passes through git's error messages

## Fallback Heuristics

If the Lingo SDK fails, `lit` uses smart fallbacks:

- If message contains "fix", "bug", "issue" → `type: fix`
- If new files are added → `type: feat`
- If only formatting changes → `type: chore`
- Default → `type: refactor`

## Tech Stack

- **Python 3.11+**: Modern Python with async support
- **Typer**: Command-line interface framework
- **rich**: Beautiful terminal output
- **questionary**: Interactive prompts
- **lingodotdev**: AI translation and analysis SDK
- **subprocess**: Direct git integration

## Development

### Install Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Quality

```bash
black lit/
ruff check lit/
mypy lit/
```

## Example Scenarios

### Scenario 1: Hinglish Commit

```bash
$ git add auth_module.py validation.py
$ lit commit -m "login ka bug fix kiya aur validation add kiya"
```

Output:
```
⟳ Translating and analyzing via Lingo.dev...

┌─────────────────────────────────────────┐
│        Commit Preview                   │
├─────────────────────────────────────────┤
│ fix: add validation checks to login     │
│                                         │
│ - implement required field validation   │
│ - resolve null pointer exception        │
│ - improve error message handling        │
└─────────────────────────────────────────┘

Commit with this message?
→ ✓ Accept
  ✏ Edit manually
  ✗ Cancel

✓ Commit successful!
fix: add validation checks to login
```

### Scenario 2: API Key Missing

```bash
$ lit commit -m "fix: add tests"
Error: LINGODOTDEV_API_KEY environment variable is not set.
Please set it to use the commit translation feature.
```

### Scenario 3: No Staged Files

```bash
$ lit commit -m "fix: cleanup"
Error: No staged files. Run git add first.
```

### Scenario 4: Regular Git Commands

```bash
$ lit status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean

$ lit log --oneline -5
a1b2c3d (HEAD -> main) fix: add validation checks to login
d4e5f6g feat: implement oauth integration
...
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-thing`)
3. Commit with conventional commits
4. Push and open a PR

## License

MIT

## Author

Built with ❤️ for developers who think differently.

---

**Tagline:** Type how you think, commit effortlessly.
