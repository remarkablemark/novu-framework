<!--
SYNC IMPACT REPORT
Version change: 0.0.0 → 1.0.0 (initial ratification)
Modified principles: N/A (initial creation)
Added sections:
- Core Principles (5 principles)
- Development Standards
- Quality Gates
- Governance
Removed sections: N/A (initial creation)
Templates requiring updates:
- ✅ plan-template.md (constitution check alignment)
- ✅ spec-template.md (scope alignment)
- ✅ tasks-template.md (task categorization)
- ✅ agent-file-template.md (guidelines)
-->

# Novu Framework Constitution

## Core Principles

### I. Library-First Design

Every feature must be implemented as a standalone, importable Python library. Libraries must be self-contained, independently testable, and fully documented. Clear functional purpose is required - no organizational-only modules or utility collections without specific use cases.

### II. Idiomatic Python

While inspired by `@novu/framework`, this project must adhere to Python best practices and idioms (PEP 8). It should not be a direct transliteration of JavaScript patterns. Interfaces must feel natural to Python developers (e.g., snake_case, decorators, context managers).

### III. Test-First Development (NON-NEGOTIABLE)

TDD is mandatory: tests must be written and approved before implementation. Follow strict Red-Green-Refactor cycle. All public APIs must have comprehensive unit tests with 100% coverage. Integration tests required for cross-component workflows.

### IV. Developer Experience (DX)

The framework must be intuitive and require minimal boilerplate. Users should be able to define workflows with simple functions. Error messages must be descriptive and actionable. "Magic" should be minimized in favor of explicit but concise configuration.

### V. Documentation Driven

Every public API (class, function, module) must have a docstring (supporting `pdoc`). Documentation should include examples. Changes to the API require corresponding documentation updates before merging.

### VI. Minimal Dependencies

Keep the dependency footprint minimal. Only add dependencies that are essential for core functionality. Prefer standard library solutions. All optional dependencies must be clearly documented and justified.

### VII. Type Safety & Standards

All code must be fully typed (Python type hints). Linting (Ruff) and formatting (Black, Isort) rules are non-negotiable and enforced via CI/pre-commit. No "type: ignore" without explicit, justified comments. Documentation strings required for all public functions and classes. Use conventional commit messages (feat:, fix:, docs:, etc.).

## Development Standards

### Code Quality

- All code must pass ruff linting and black formatting
- Type hints required for all public interfaces
- Documentation strings required for all public functions and classes
- Use conventional commit messages (feat:, fix:, docs:, etc.)

### Testing Requirements

- Unit tests for all core logic
- Integration tests for notification workflow end-to-end scenarios
- Performance tests for high-volume notification scenarios
- Contract tests for API compatibility

### Versioning Policy

- Follow Semantic Versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes to public APIs
- MINOR: New features, backward-compatible additions
- PATCH: Bug fixes, documentation improvements
- All versions must be tested for backward compatibility

## Quality Gates

### Pre-commit Requirements

- Code must pass all linting checks
- All tests must pass with adequate coverage
- Documentation must build successfully
- No security vulnerabilities in dependencies

### Release Criteria

- All tests passing in CI/CD
- Documentation updated and accurate
- Changelog maintained with version notes
- Performance benchmarks meet defined thresholds

## Governance

This constitution supersedes all other development practices. Amendments require:

- Documentation of proposed changes
- Team review and approval
- Migration plan for existing code
- Version bump according to semantic versioning rules

All pull requests and code reviews must verify compliance with these principles. Complexity must be explicitly justified with reference to these principles. Use this constitution as the primary guidance for all development decisions.

**Version**: 1.0.0 | **Ratified**: 2026-01-20 | **Last Amended**: 2026-01-20
