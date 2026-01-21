---
description: "Implementation tasks for Python Framework Package"
---

# Tasks: Python Framework Package

**Input**: Design documents from `/specs/001-python-framework/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md
**Constitution Compliance**: Library-First Design, Pythonic Interface, Test-First Development, Minimal Dependencies

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize project structure and tooling

- [ ] T001 Create project structure (src/novu_framework, tests)
- [ ] T002 Initialize pyproject.toml with dependencies (pydantic, fastapi)
- [ ] T003 [P] Configure pytest, mypy, and ruff in pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and base types

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create base exceptions in src/novu_framework/exceptions.py
- [ ] T005 [P] Define ControlSchema validation in src/novu_framework/validation/controls.py
- [ ] T006 [P] Define Payload validation in src/novu_framework/validation/payload.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Basic Workflow Definition (Priority: P1)

**Goal**: Enable developers to define and trigger simple workflows using decorators

**Independent Test**: Create a workflow with a single step and trigger it programmatically

### Implementation for User Story 1

- [ ] T008 [US1] Implement Workflow class registry in src/novu_framework/workflow.py
  - Copy approach from https://github.com/novuhq/novu/blob/v3.12.0/packages/framework/src/resources/workflow/workflow.resource.ts
- [ ] T009 [US1] Implement @workflow decorator in src/novu_framework/workflow.py
- [ ] T010 [US1] Implement basic trigger() method in src/novu_framework/workflow.py
- [ ] T011 [US1] Test workflow registration in tests/unit/test_workflow_registry.py
- [ ] T012 [US1] Test basic trigger execution in tests/unit/test_trigger.py

**Checkpoint**: User Story 1 fully functional (workflows can be defined and triggered)

---

## Phase 4: User Story 2 - Multi-Step Workflows (Priority: P1)

**Goal**: Support complex workflows with multiple step types (in-app, email)

**Independent Test**: Execute a workflow with in-app and email steps in order

### Implementation for User Story 2

- [ ] T013 [P] [US2] Create BaseStep abstract class in src/novu_framework/steps/base.py
- [ ] T014 [P] [US2] Implement InAppStep in src/novu_framework/steps/in_app.py
- [ ] T015 [P] [US2] Implement EmailStep in src/novu_framework/steps/email.py
- [ ] T016 [P] [US2] Implement SmsStep in src/novu_framework/steps/sms.py
- [ ] T017 [P] [US2] Implement PushStep in src/novu_framework/steps/push.py
- [ ] T018 [US2] Update Workflow execution engine to handle step sequences in src/novu_framework/workflow.py
- [ ] T019 [US2] Implement step skip logic in src/novu_framework/steps/base.py
- [ ] T020 [US2] Integration test for multi-step execution in tests/integration/test_workflow_execution.py

**Checkpoint**: User Story 2 functional (complex workflows with steps)

---

## Phase 5: User Story 3 - Framework Integration (Priority: P2)

**Goal**: Serve workflows via FastAPI endpoints

**Independent Test**: Start FastAPI app and verify workflow endpoints are reachable

### Implementation for User Story 3

- [ ] T022 [P] [US3] Create API contract models in src/novu_framework/validation/api.py
- [ ] T023 [US3] Implement serve() function in src/novu_framework/fastapi.py
- [ ] T024 [US3] Implement route handlers for workflow discovery and execution in src/novu_framework/fastapi.py
- [ ] T025 [US3] Contract test for API endpoints in tests/contract/test_api_contract.py
- [ ] T026 [US3] Integration test with FastAPI app in tests/integration/test_fastapi.py

**Checkpoint**: User Story 3 functional (HTTP API available)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, final validation, and cleanup

- [ ] T027 [P] Create README.md with installation and usage guide
- [ ] T028 [P] Validate code against quickstart.md examples
- [ ] T029 Ensure 100% type hint coverage with mypy
- [ ] T030 Run full test suite and verify coverage

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Phase 1
- **User Stories (Phase 3+)**: Depend on Foundational Phase
  - US1 and US2 are P1, but US2 depends on basic workflow structure from US1 logic (conceptually), though they can share foundational types.
  - Recommended: Phase 3 (US1) -> Phase 4 (US2) -> Phase 5 (US3)

### Parallel Opportunities

- Steps implementation (T013-T018) in Phase 4 can be parallelized
- Setup tasks (T001-T003) can be parallelized
- Validation models (T005-T006) can be parallelized

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Setup & Foundational
2. Implement Basic Workflow (US1)
3. Implement Step definitions (US2)
4. Verify local execution

### Integration (US3)

1. Add FastAPI integration
2. Verify HTTP endpoints
