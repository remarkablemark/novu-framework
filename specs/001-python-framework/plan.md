# Implementation Plan: Python Framework Package

**Branch**: `001-python-framework` | **Date**: 2026-01-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-python-framework/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a Python package that emulates the npm TypeScript @novu/framework, providing code-first notification workflow capabilities. The framework will enable Python developers to define notification workflows using decorators, execute multi-step workflows (in_app, email, sms, push), and integrate with FastAPI for HTTP endpoint serving. The implementation will follow Pythonic patterns while maintaining the core workflow concepts from the TypeScript version.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: pydantic
**Testing**: pytest with async support
**Target Platform**: Linux/macOS/Windows servers
**Project Type**: single (Python library package)
**Performance Goals**: 1000 concurrent workflow triggers, <50ms FastAPI integration overhead
**Constraints**: <200ms workflow execution, minimal memory footprint
**Scale/Scope**: Enterprise notification workflows, high-volume event processing

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

### Required Compliance

- [x] **Library-First Design**: Feature can be implemented as standalone, importable module
- [x] **Pythonic Interface**: Clean PEP 8 compliant API with type hints
- [x] **Test-First Approach**: Testable design with 100% coverage feasibility
- [x] **Domain Focus**: Directly supports notification workflow patterns
- [x] **Minimal Dependencies**: No unnecessary external dependencies

### Post-Design Evaluation

All constitution requirements satisfied with the final design:

✅ **Library-First Design**: Modular package structure with clear imports (`from novu_framework import workflow`)

✅ **Pythonic Interface**: Decorator-based workflow definition, async/await patterns, Pydantic validation, PEP 8 naming conventions

✅ **Test-First Approach**: Comprehensive testing strategy with unit, integration, and performance tests defined

✅ **Domain Focus**: Direct mapping to notification workflow patterns (in_app, email, sms, push steps)

✅ **Minimal Dependencies**: Only essential dependencies with standard library alternatives where possible

### Complexity Justification

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation                     | Why Needed                          | Simpler Alternative Rejected Because |
| ----------------------------- | ----------------------------------- | ------------------------------------ |
| [e.g., additional dependency] | [specific notification requirement] | [why standard library insufficient]  |
| [e.g., complex architecture]  | [specific workflow need]            | [why simpler approach insufficient]  |

## Project Structure

### Documentation (this feature)

```text
specs/001-python-framework/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/novu_framework/
├── __init__.py           # Exports: workflow
├── workflow.py           # Workflow decorator and core logic
├── steps/                # Step implementations
│   ├── __init__.py
│   ├── base.py           # Base step class
│   ├── in_app.py         # In-app notification step
│   ├── email.py          # Email notification step
│   ├── sms.py            # SMS notification step
│   └── push.py           # Push notification step
├── fastapi.py            # FastAPI integration (exports: serve, Client)
└── validation/           # Schema validation
    ├── __init__.py
    ├── payload.py        # Payload validation
    └── controls.py       # Control schema validation

tests/
├── unit/                 # Unit tests for core logic
├── integration/          # Integration tests for workflows
├── contract/             # Contract tests for API compatibility
└── performance/          # Performance tests for high-volume scenarios
```

**Structure Decision**: Single Python library package with modular components. The structure follows Python packaging best practices with clear separation of concerns: workflow definition, step implementations, framework integration, validation, and execution engine. This supports the Library-First Design principle while enabling independent testing and development of components.
