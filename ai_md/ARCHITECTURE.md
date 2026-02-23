# Architecture & Design Document for `lit`

## Overview

`lit` is a Python CLI tool that wraps `git` and provides **intelligent commit message generation** using AI translation and diff analysis.

**Core Philosophy:**
- Behave exactly like `git` for all commands
- Only intercept `lit commit` to apply translation + Conventional Commits
- Fail gracefully with helpful fallbacks

## High-Level Architecture

```
User Input (CLI)
    ↓
Typer Router (cli.py)
    ├─→ "commit" → Commit Flow (async)
    └─→ anything else → Git Passthrough
```

## Module Design

### 1. `cli.py` - Command Router

**Responsibility:** Route commands to either commit flow or git passthrough.

**Key Functions:**
- `main(ctx: typer.Context)`: Entry point that inspects `sys.argv[1]`
- `_handle_commit(args)`: Extracts `-m` message and triggers async flow

**Flow:**
```python
if args[0] == "commit":
    message = extract_message_from_args(args)
    asyncio.run(run_commit_flow(message))
else:
    subprocess.run(["git"] + args)  # Passthrough
```

**Why Typer?**
- Minimal overhead for router
- Clean CLI interface
- Easy to extend with more commands later

---

### 2. `git_utils.py` - Git Operations

**Responsibility:** Subprocess wrappers for git commands.

**Key Functions:**
- `is_git_repo()`: Check if inside git repository
- `get_staged_files()`: Get list of staged files
- `get_staged_diff()`: Get unified diff of staged changes
- `commit_with_message(title, body)`: Final commit execution
- `passthrough_git_command()`: Execute git with all arguments
- `get_git_root()`: Get repository root directory

**Design Decisions:**
- Uses `subprocess.run()` with `check=True` for error handling
- Returns clean types (list[str], str, bool)
- Raises `RuntimeError` with descriptive messages
- Captures stdout/stderr for analysis

**Example:**
```python
def get_staged_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout
```

---

### 3. `lingo_utils.py` - Translation & Parsing

**Responsibility:** Integrate with Lingo.dev SDK and parse responses.

**Key Components:**

#### `ConventionalCommit` Dataclass
```python
@dataclass
class ConventionalCommit:
    type: str      # "feat", "fix", "refactor", etc.
    title: str     # Under 72 chars
    body: str      # Detailed explanation
    
    def format_message(self) -> Tuple[str, str]:
        return f"{type}: {title}", body
```

#### `translate_commit_message()` - Async Translation

**Flow:**
```python
async def translate_commit_message(raw_message, staged_diff):
    1. Get API key from env
    2. Prepare content object with:
       - system instruction (embedded)
       - raw_message
       - diff
    3. Call Lingo SDK:
       async with LingoDotDevEngine(...) as engine:
           result = await engine.localize_object(content, config)
    4. Parse JSON response
    5. Validate constraints
    6. Return ConventionalCommit or None
```

**Why Async?**
- Lingo SDK is async
- Non-blocking network I/O
- Allows spinner animation while waiting

#### `parse_lingo_response()`

**Robustness:**
1. Uses regex to extract JSON (handles surrounding text)
2. Strict validation:
   - All required fields present
   - Valid commit type
   - Title under 72 chars
   - Body not empty
3. Returns `None` if invalid (triggers fallback)

**Example:**
```python
response = """
Some text...
{
    "type": "fix",
    "title": "correct login validation",
    "body": "add required checks"
}
More text...
"""
# Regex extracts the JSON, parses it, validates, returns ConventionalCommit
```

#### `fallback_generate_commit()` - Heuristic Generation

**Strategy:**
- Analyzes keywords in message and diff
- Assigns type based on patterns
- Creates basic title and body

**Keyword Patterns:**
- **fix**: "fix", "bug", "issue", "correct", "resolve"
- **feat**: "feat", "new", "add", "feature" OR "new file:" in diff
- **chore**: "whitespace", "formatting", "style" in diff
- **default**: refactor

---

### 4. `commit_flow.py` - Orchestration

**Responsibility:** Coordinate the entire commit workflow.

**Main Function:**
```python
async def run_commit_flow(raw_message: str) -> bool:
```

**Flow Steps:**

```
1. VALIDATION
   ├─ is_git_repo() → error if false
   ├─ get_staged_files() → error if empty
   └─ get_staged_diff() → warn if empty

2. TRANSLATION (with spinner)
   ├─ Call translate_commit_message()
   └─ Fallback if fails

3. PREVIEW
   └─ Display rich Panel with formatted commit

4. CONFIRMATION
   └─ questionary.select() → Accept/Edit/Cancel

5. EDIT (if selected)
   ├─ questionary.text() for title
   ├─ questionary.text() for body
   └─ Create new ConventionalCommit

6. COMMIT
   └─ commit_with_message(title, body)
   └─ git commit -m "type: title" -m "body"

7. SUCCESS MESSAGE
   └─ "✓ Commit successful!"
```

**Error Handling:**
- `CommitFlowError`: Custom exception for flow errors
- Try-catch around SDK calls
- Fallback to heuristics
- User-friendly error messages with `rich` styling

---

### 5. `__main__.py` - Entry Point

**Responsibility:** Single-line entry point.

**Code:**
```python
def main() -> None:
    """Main entry point for the lit CLI."""
    app()  # Calls cli.app()

if __name__ == "__main__":
    main()
```

**Why separate?**
- Clean separation of concerns
- Allows `lit` package to be imported
- Entry point in `pyproject.toml`: `lit = "lit.__main__:main"`

---

## Data Flow

### Git Passthrough Command
```
User: lit status
    ↓
cli.py: args[0] != "commit"
    ↓
git_utils.passthrough_git_command()
    ↓
subprocess.run(["git", "status"])
    ↓
Output streamed directly
```

### Commit Command
```
User: lit commit -m "login ka bug fix"
    ↓
cli.py: args[0] == "commit", extract message
    ↓
asyncio.run(commit_flow.run_commit_flow(message))
    ↓
commit_flow.py:
    ├─ Check git repo ✓
    ├─ Check staged files ✓
    ├─ Get diff → "fixed 3 lines in auth.py"
    ├─ Show spinner
    └─ Call Lingo SDK
    
lingo_utils.py:
    ├─ Send to SDK with instruction
    ├─ Receive: '{"type": "fix", "title": "...", "body": "..."}'
    ├─ Parse JSON
    └─ Return ConventionalCommit
    
commit_flow.py:
    ├─ Show preview
    ├─ Ask confirmation (Accept/Edit/Cancel)
    ├─ If Accept: call git_utils.commit_with_message()
    ├─ git commit -m "fix: correct login validation" -m "body"
    └─ Show success message
```

---

## Error Handling Strategy

### Explicit Errors (User Action)

**No Staged Files**
```
→ "No staged files. Run git add first."
```

**Not in Git Repo**
```
→ "Not inside a git repository."
```

**Commit without -m**
```
→ "Commit requires a message. Use: lit commit -m \"message\""
```

### SDK Errors (With Fallback)

**Missing API Key**
```
→ RuntimeError caught
→ Use fallback heuristic
→ Show warning
→ Continue with generated commit
```

**Network Error**
```
→ RuntimeError/RuntimeException caught
→ Use fallback heuristic
→ Show warning: "Translation failed: [error]. Using heuristic generation as fallback."
→ Continue
```

**Invalid JSON**
```
→ parse_lingo_response() returns None
→ Fall back to fallback_generate_commit()
→ Show warning
→ Continue
```

### User Interruption

**Ctrl+C**
```
→ KeyboardInterrupt caught
→ "Interrupted by user."
→ Exit cleanly
```

**Cancel Confirmation**
```
→ questionary returns None
→ "Commit cancelled."
→ Return False
```

---

## Type System

**Key Type Hints:**
```python
# Return types
is_git_repo() -> bool
get_staged_files() -> list[str]
get_staged_diff() -> str
passthrough_git_command() -> int
translate_commit_message(...) -> Optional[ConventionalCommit]
run_commit_flow(...) -> bool

# Parameters
format_message(self) -> Tuple[str, str]
parse_lingo_response(response: str) -> Optional[ConventionalCommit]
```

**Why Type Hints?**
- Self-documenting code
- IDE autocompletion
- Static type checking with mypy
- Reduces bugs

---

## Async Handling

**Why Async for Lingo SDK?**
- SDK is `async/await` native
- Network I/O is non-blocking
- Allows spinner animation while waiting

**Event Loop Management:**
```python
# In cli.py
asyncio.run(run_commit_flow(message))
```

**Async Context Manager:**
```python
# In lingo_utils.py
async with LingoDotDevEngine(...) as engine:
    result = await engine.localize_object(...)
```

---

## Testing Strategy

### Unit Tests (`tests/test_lit.py`)

1. **Validation Tests**
   - Valid/invalid commit types
   - Title length constraints
   - Title period validation

2. **JSON Parsing Tests**
   - Valid JSON response
   - JSON with surrounding text
   - Invalid JSON (fallback)
   - Missing fields (fallback)

3. **Fallback Tests**
   - Keyword detection
   - Type assignment
   - Message truncation

4. **Edge Cases**
   - Empty messages
   - Very long messages
   - Unicode characters

### Integration Tests (Future)
- Full commit flow with mocked SDK
- Git command passthrough
- Error conditions

### Manual Testing
- Real commits in test repository
- With and without API key
- Various message languages
- Git command verification

---

## Extensibility

### Adding New Git Commands

If `lit` needs to support more special commands:

```python
# In cli.py
if args[0] == "commit":
    _handle_commit(args)
elif args[0] == "rebase":
    _handle_rebase(args)  # New special handler
else:
    passthrough_git_command()
```

### Customizing SDK Instruction

```python
# In lingo_utils.py
system_instruction = """
[Your custom instruction here]
"""
```

### Adding Commit Type Validation

```python
# In lingo_utils.py
ALLOWED_TYPES = {"feat", "fix", "refactor", ...}

def validate_conventional_commit_type(commit_type: str) -> bool:
    return commit_type.lower() in ALLOWED_TYPES
```

---

## Performance Considerations

### Caching (Not Implemented Yet)
- Could cache Lingo responses for identical diffs
- Would reduce API calls for repeated changes

### Timeout Handling
- SDK calls should have timeout (future enhancement)
- Fallback on timeout

### Subprocess Efficiency
- Direct `subprocess.run()` (minimal overhead)
- No shell=True (security + efficiency)

---

## Security Considerations

1. **API Key Handling**
   - Reads from environment variable (not hardcoded)
   - Never logged or displayed

2. **Shell Injection**
   - Uses `subprocess.run(["git", ...])` (list form)
   - Not using `shell=True`
   - Arguments not interpolated

3. **JSON Parsing**
   - Uses `json.loads()` (safe)
   - Validates all fields before use

4. **Error Messages**
   - Don't leak sensitive paths in error output
   - Show helpful messages without exposing internals

---

## Deployment

### As PyPI Package
```bash
python -m build
twine upload dist/
```

### Command Entry Point
```toml
# pyproject.toml
[project.scripts]
lit = "lit.__main__:main"
```

### Installation
```bash
pip install lit-cli
lit --help
```

---

## Future Enhancements

1. **Local Model Support**
   - Fallback to Ollama/local LLM if API unavailable

2. **Configuration File**
   - `~/.lit/config.yaml` for custom instructions

3. **Commit Templates**
   - User-defined templates for specific project types

4. **Analytics**
   - Track commit types distribution
   - Suggest improvements

5. **Integration Hooks**
   - Pre-commit hooks that use `lit`
   - GitHub Actions integration

6. **Multiple Languages**
   - Support more language pairs
   - Language-specific commit conventions

---

## Maintenance

### Code Quality
- Black for formatting
- Ruff for linting
- MyType for type checking

### Documentation
- Docstrings for all functions
- Type hints throughout
- README with examples
- QUICKSTART for setup

### Testing
- pytest for unit tests
- Manual integration testing
- GitHub Actions CI/CD (future)

---

This architecture ensures `lit` is:
- ✅ Production-ready
- ✅ Maintainable
- ✅ Extensible
- ✅ User-friendly
- ✅ Reliable (with fallbacks)
