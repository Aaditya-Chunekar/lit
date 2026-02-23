.PHONY: help install install-dev test lint format type-check clean build publish demo

help:
	@echo "lit - Type how you think, commit effortlessly"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       Install lit in production mode"
	@echo "  make install-dev   Install lit with development tools"
	@echo "  make test          Run unit tests"
	@echo "  make lint          Run code linting"
	@echo "  make format        Format code with black"
	@echo "  make type-check    Check types with mypy"
	@echo "  make clean         Remove build artifacts"
	@echo "  make build         Build distribution packages"
	@echo "  make publish       Publish to PyPI (requires TWINE_TOKEN)"
	@echo "  make demo          Run interactive demo"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --cov=lit --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	ruff check lit tests

format:
	black lit tests

type-check:
	mypy lit

quality: format lint type-check test
	@echo "All quality checks passed!"

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -r {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -r {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	rm -rf build dist *.egg-info 2>/dev/null || true

build: clean
	python -m build

publish: build
	twine upload dist/* --skip-existing

demo:
	@echo "Setting up demo repository..."
	@mkdir -p /tmp/lit-demo && cd /tmp/lit-demo && git init
	@echo "# Demo Repository" > /tmp/lit-demo/README.md
	@cd /tmp/lit-demo && git add README.md
	@echo ""
	@echo "Demo ready! Try:"
	@echo "  cd /tmp/lit-demo"
	@echo "  lit commit -m \"initial commit\""
	@echo ""
	@echo "Or run these commands manually:"
	@echo "  mkdir -p test-repo && cd test-repo"
	@echo "  git init"
	@echo "  echo '# Test' > README.md"
	@echo "  git add README.md"
	@echo "  lit commit -m \"add readme\""

.DEFAULT_GOAL := help
