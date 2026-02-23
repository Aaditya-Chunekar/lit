# lit 🔥

**Type how you think, commit effortlessly.**

`lit` is an AI-powered git wrapper that translates your natural language (even Hinglish!) into clean, conventional commits. All other git commands work exactly as expected.

## Features

- ✨ AI-powered commit message generation
- 🌍 Multi-language support (Hinglish, English, etc.)
- 📝 Conventional Commits format
- 🎯 Smart commit type detection
- 🚀 Zero-config git proxy
- 💅 Beautiful interactive prompts

## Installation

```bash
npm install -g lit
```

Or run locally:

```bash
npm install
npm link
```

## Configuration

Create a `.env` file:

```bash
LINGO_API_URL=https://api.lingo.dev/v1/generate
LINGO_API_KEY=your_api_key_here
```

## Usage

### AI-Powered Commits

```bash
# Stage your files
lit add .

# Commit with natural language
lit commit -m "login bug fix aur validation add kiya"

# Output:
# fix: correct login validation logic
#
# - add required field checks
# - resolve authentication flow issue
```

### All Other Git Commands (Proxied)

```bash
lit status
lit push origin main
lit checkout -b feature/new-feature
lit log --oneline
lit branch
lit pull
```

Everything works exactly like `git`!

## How It Works

1. You stage files normally: `lit add .`
2. Run commit with natural language: `lit commit -m "your message"`
3. `lit` analyzes your diff and translates your message
4. Review the generated conventional commit
5. Accept, edit, or cancel

## API Integration

`lit` uses the Lingo.dev API for intelligent translation and diff analysis. If the API is unavailable, it falls back to smart heuristics.

## Fallback Behavior

Without API credentials, `lit` uses built-in heuristics:
- Keyword detection (fix, feat, docs, etc.)
- Diff analysis (file patterns, change ratios)
- Smart commit type classification

## Requirements

- Node.js >= 18
- Git installed and configured

## Tech Stack

- Node.js ES Modules
- commander (CLI framework)
- simple-git (Git operations)
- @clack/prompts (Interactive UI)
- picocolors (Terminal colors)
- Native fetch (HTTP requests)

## License

MIT

## Contributing

Contributions welcome! This is a hackathon project built for real-world use.
