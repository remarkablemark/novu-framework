# Implementation Plan: Flask Support

**Branch**: `001-flask-support` | **Date**: 2026-01-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-flask-support/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add Flask web framework support to novu-framework, providing equivalent functionality to the existing FastAPI integration. This includes creating a Flask integration module with health check and workflow execution endpoints, maintaining 100% API compatibility with existing workflow definitions, and ensuring proper error handling and async execution within Flask's synchronous context.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.10+
**Primary Dependencies**: Flask, Flask's async support, existing novu-framework core
**Storage**: N/A (stateless web endpoints)
**Testing**: pytest with Flask test client
**Target Platform**: Linux/macOS/Windows servers
**Project Type**: Single Python library
**Performance Goals**: <200ms response time, 1000 req/s throughput
**Constraints**: Must maintain compatibility with existing FastAPI integration
**Scale/Scope**: Support for existing workflow definitions without modification

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

### Required Compliance

- [x] **Library-First Design**: Feature can be implemented as standalone, importable module
- [x] **Pythonic Interface**: Clean PEP 8 compliant API with type hints
- [x] **Test-First Approach**: Testable design with 100% coverage feasibility
- [x] **Domain Focus**: Directly supports notification workflow patterns
- [x] **Minimal Dependencies**: Only Flask as additional dependency

### Complexity Justification

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation                     | Why Needed                          | Simpler Alternative Rejected Because |
| ----------------------------- | ----------------------------------- | ------------------------------------ |
| [e.g., additional dependency] | [specific notification requirement] | [why standard library insufficient]  |
| [e.g., complex architecture]  | [specific workflow need]            | [why simpler approach insufficient]  |

## Project Structure

### Documentation (this feature)

```text
specs/001-flask-support/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── novu_framework/
│   ├── fastapi.py        # Existing FastAPI integration
│   ├── flask.py          # NEW: Flask integration module
│   ├── workflow.py       # Core workflow functionality
│   ├── validation/
│   │   └── api.py        # Shared validation models
│   └── ...

tests/
├── contract/
│   └── test_api_contract.py  # Shared API contract tests
├── integration/
│   ├── test_fastapi.py       # Existing FastAPI tests
│   └── test_flask.py         # NEW: Flask integration tests
├── unit/
│   ├── test_base_step.py     # Existing unit tests
│   └── test_flask.py         # NEW: Flask module unit tests
└── ...
```

**Structure Decision**: Single Python library structure following existing patterns. Flask integration will be added as `src/novu_framework/flask.py` alongside existing FastAPI integration. Tests will follow the same structure with unit, integration, and contract tests.

## Phase 1 Complete: Design & Contracts

### Generated Artifacts

✅ **research.md** - Technical research and decision documentation
✅ **data-model.md** - Data model analysis and flow documentation
✅ **contracts/openapi.yaml** - Complete API specification
✅ **quickstart.md** - Comprehensive getting started guide

### Design Decisions Confirmed

- **Flask Integration Pattern**: Mirror FastAPI with Blueprint structure
- **Async Support**: Use Flask 2.0+ native async routes
- **API Compatibility**: 100% compatible with FastAPI integration
- **Error Handling**: Consistent JSON error responses
- **Testing Strategy**: Flask test client with pytest

### Constitution Compliance Re-verified

All constitutional requirements satisfied:

- Library-First Design ✅
- Pythonic Interface ✅
- Test-First Approach ✅
- Domain Focus ✅
- Minimal Dependencies ✅

### Ready for Phase 2

The design phase is complete with all technical decisions made and documented. The implementation plan is ready for task generation via `/speckit.tasks`.
