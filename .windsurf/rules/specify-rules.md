# Novu Framework Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-20

## Constitution Principles

### Core Requirements

- **Library-First Design**: All features as standalone, importable modules
- **Pythonic Interface**: PEP 8 compliant APIs with type hints
- **Test-First Development**: TDD mandatory with 100% coverage
- **Domain Focus**: Direct notification workflow support only
- **Minimal Dependencies**: Essential dependencies only, well-justified

### Development Standards

- Code quality: ruff linting, black formatting, type hints
- Testing: unit, integration, performance, and contract tests
- Versioning: Semantic Versioning (MAJOR.MINOR.PATCH)
- Documentation: Comprehensive docs for all public APIs

## Active Technologies

- Python 3.10+ (001-python-framework)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

### Python Standards

- Follow PEP 8 conventions
- Use black for formatting
- Use ruff for linting
- Type hints required for public interfaces
- Docstrings required for all public functions/classes

### Testing Standards

- pytest for unit tests
- > 90% coverage requirement
- Integration tests for workflows
- Performance tests for high-volume scenarios

## Recent Changes

- 001-python-framework: Added Python 3.10+

<!-- MANUAL ADDITIONS START -->

### Constitution Reference

Always consult `.specify/memory/constitution.md` for development decisions. This constitution supersedes all other practices.

<!-- MANUAL ADDITIONS END -->
