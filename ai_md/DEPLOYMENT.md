# Deployment & Build Guide for `lit`

## Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/lit.git
cd lit
```

### 2. Create Virtual Environment
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n lit python=3.11
conda activate lit
```

### 3. Install in Development Mode
```bash
pip install -e ".[dev]"
```

This installs:
- Core dependencies (typer, rich, questionary, lingodotdev)
- Dev dependencies (pytest, black, ruff, mypy)

### 4. Set Environment Variable
```bash
export LINGODOTDEV_API_KEY="your-api-key"
# Or on Windows:
set LINGODOTDEV_API_KEY=your-api-key
```

### 5. Verify Installation
```bash
lit --help
```

---

## Testing

### Run Unit Tests
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_lit.py::TestConventionalCommitValidation -v
```

### Run with Coverage
```bash
pytest tests/ --cov=lit --cov-report=html
```

### Type Checking
```bash
mypy lit/
```

### Code Formatting
```bash
black lit/ tests/
```

### Linting
```bash
ruff check lit/ tests/
```

### All Quality Checks
```bash
#!/bin/bash
black lit/ tests/
ruff check lit/ tests/
mypy lit/
pytest tests/ -v
```

---

## Manual Testing

### Test 1: Basic Git Commands
```bash
cd /tmp && mkdir test-lit-demo && cd test-lit-demo
git init
lit status
```

Should output: `On branch main`, `nothing to commit`

### Test 2: Staging and Commit
```bash
# Create a file
echo "# Test Repo" > README.md
git add README.md

# Stage the file
lit status
# Should show: "Changes to be committed"

# Test commit (with fallback, if no API key)
lit commit -m "add readme file"
```

### Test 3: More Complex Scenario
```bash
# Create multiple files
echo "main code" > main.py
echo "test" > test.py
git add .

# Commit with mixed language message
lit commit -m "bug fix kiya aur tests add kiye"
```

### Test 4: Verify Commit
```bash
lit log --oneline
```

---

## Building for Distribution

### Prerequisites
```bash
pip install build twine
```

### Build Distribution Packages
```bash
python -m build
```

This creates:
- `dist/lit_cli-0.1.0.tar.gz` (source distribution)
- `dist/lit_cli-0.1.0-py3-none-any.whl` (wheel)

### Verify Build
```bash
twine check dist/*
```

### Upload to PyPI (Production)

**First time setup:**
```bash
# Create account at https://pypi.org
# Create ~/.pypirc:
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository: https://test.pypi.org/legacy/
username: __token__
password: pypi-AgEIcHlwaS5vcmc...  # Your token

[pypi]
repository: https://upload.pypi.org/legacy/
username: __token__
password: pypi-AgEIcHlwaS5vcmc...  # Your token
```

**Upload to TestPyPI (recommended first):**
```bash
twine upload --repository testpypi dist/*
```

**Verify on TestPyPI:**
```bash
pip install -i https://test.pypi.org/simple/ lit-cli
```

**Upload to Real PyPI:**
```bash
twine upload dist/*
```

---

## Docker Deployment (Optional)

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install git (required for lit)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install lit
RUN pip install -e .

# Set environment
ENV LINGODOTDEV_API_KEY=""

ENTRYPOINT ["lit"]
```

### Build Docker Image
```bash
docker build -t lit:latest .
```

### Run in Docker
```bash
docker run -e LINGODOTDEV_API_KEY="your-key" -v $(pwd):/work lit commit -m "test"
```

---

## GitHub Actions CI/CD

### Create `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Lint with black
      run: black --check lit tests
    
    - name: Check with ruff
      run: ruff check lit tests
    
    - name: Type check with mypy
      run: mypy lit
    
    - name: Run tests
      run: pytest tests/ -v

  publish:
    needs: test
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install build dependencies
      run: pip install build twine
    
    - name: Build distribution
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
      run: twine upload dist/*
```

---

## Versioning

### Update Version

1. **Update in `pyproject.toml`:**
```toml
[project]
version = "0.2.0"
```

2. **Update in `lit/__init__.py`:**
```python
__version__ = "0.2.0"
```

3. **Create Git Tag:**
```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### Semantic Versioning
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

---

## Release Checklist

- [ ] Update version in `pyproject.toml` and `__init__.py`
- [ ] Update `CHANGELOG.md` (if exists)
- [ ] Run full test suite: `pytest`
- [ ] Check code quality: `black`, `ruff`, `mypy`
- [ ] Update `README.md` if needed
- [ ] Build distribution: `python -m build`
- [ ] Verify build: `twine check dist/*`
- [ ] Create git tag: `git tag v0.2.0`
- [ ] Push tag: `git push origin v0.2.0`
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Verify on PyPI: https://pypi.org/project/lit-cli/

---

## Installation Methods

### Method 1: From PyPI (Users)
```bash
pip install lit-cli
```

### Method 2: From Source (Development)
```bash
git clone https://github.com/yourusername/lit.git
cd lit
pip install -e .
```

### Method 3: With Development Tools
```bash
pip install -e ".[dev]"
```

### Method 4: Docker
```bash
docker run -e LINGODOTDEV_API_KEY="key" -v $(pwd):/work lit commit -m "msg"
```

---

## Troubleshooting

### Issue: `lit` command not found
```bash
# Verify installation
pip show lit-cli

# Reinstall in development mode
pip install -e .

# Check if script is in PATH
which lit  # or where lit on Windows
```

### Issue: Import errors
```bash
# Reinstall all dependencies
pip install -r requirements.txt

# Clear cache and reinstall
pip cache purge
pip install -e .
```

### Issue: Tests failing
```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests with verbose output
pytest tests/ -v -s

# Run specific test
pytest tests/test_lit.py::TestConventionalCommitValidation::test_valid_commit_type -v
```

### Issue: `LINGODOTDEV_API_KEY` not recognized
```bash
# Check if env var is set
echo $LINGODOTDEV_API_KEY  # Unix
echo %LINGODOTDEV_API_KEY%  # Windows

# Set it properly
export LINGODOTDEV_API_KEY="your-key"  # Unix
set LINGODOTDEV_API_KEY=your-key  # Windows
setx LINGODOTDEV_API_KEY "your-key"  # Windows (persistent)
```

---

## Post-Release

1. **Update GitHub Releases**
   - Go to https://github.com/yourusername/lit/releases
   - Create release from tag
   - Add release notes

2. **Announce on Social Media**
   - Tweet about new release
   - Share on relevant communities

3. **Monitor Issues**
   - Watch for bug reports
   - Respond to GitHub issues

---

## Maintenance Timeline

- **Weekly**: Check for dependency updates
- **Monthly**: Security patches review
- **Quarterly**: Feature releases
- **Annually**: Major version bump

---

This guide ensures `lit` is professionally deployed and maintained!
