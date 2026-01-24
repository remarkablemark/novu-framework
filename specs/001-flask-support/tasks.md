---
description: "Task list template for feature implementation"
---

# Tasks: Flask Support

**Input**: Design documents from `/specs/001-flask-support/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Constitution Compliance**: All tasks must follow Library-First Design, Pythonic Interface, Test-First Development, and Minimal Dependencies principles.

**Testing**: Constitution mandates comprehensive testing - unit tests (100% coverage), integration tests for workflows, performance tests for high-volume scenarios, and contract tests for API compatibility.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Task Categories (Constitution-Aligned)

### Library Design Tasks

- Module structure and interface design
- API definition with type hints
- Dependency analysis and justification

### Testing Tasks (Mandatory)

- Unit test implementation (100% coverage required)
- Integration test setup for workflows
- Performance test scenarios
- Contract test definitions

### Implementation Tasks

- Core functionality implementation
- CLI interface (if applicable)
- Documentation and examples

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create Flask integration module structure in src/novu_framework/flask.py
- [x] T002 Add Flask as optional dependency to pyproject.toml with extras [flask]
- [x] T003 [P] Configure Flask-specific imports and type hints in src/novu_framework/flask.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Flask Blueprint structure for route organization in src/novu_framework/flask.py
- [x] T005 [P] Implement workflow registry for Flask app context in src/novu_framework/flask.py
- [x] T006 [P] Setup Flask error handlers with JSON response formatting in src/novu_framework/flask.py
- [x] T007 Create async route wrapper functions for workflow execution in src/novu_framework/flask.py
- [x] T008 Configure request/response validation using existing Pydantic models in src/novu_framework/flask.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Flask Integration (Priority: P1) 🎯 MVP

**Goal**: Provide Flask integration with health check and workflow execution endpoints

**Independent Test**: Create Flask app, register workflows, make HTTP requests to verify endpoints work correctly

### Tests for User Story 1 (Constitution Mandated) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Contract test for health check endpoint in tests/contract/test_api_contract.py
- [x] T010 [P] [US1] Contract test for workflow execution endpoint in tests/contract/test_api_contract.py
- [x] T011 [P] [US1] Integration test for Flask app setup in tests/integration/test_flask.py
- [x] T012 [P] [US1] Integration test for workflow discovery in tests/integration/test_flask.py
- [x] T013 [P] [US1] Integration test for workflow execution in tests/integration/test_flask.py

### Implementation for User Story 1

- [x] T014 [US1] Implement health check endpoint in src/novu_framework/flask.py (depends on T004, T008)
- [x] T015 [US1] Implement workflow execution endpoint in src/novu_framework/flask.py (depends on T007, T014)
- [x] T016 [US1] Create serve() function for Flask app integration in src/novu_framework/flask.py (depends on T005, T015)
- [x] T017 [US1] Add workflow discovery logic using existing AST analysis in src/novu_framework/flask.py (depends on T014)
- [x] T018 [US1] Implement async workflow execution within Flask context in src/novu_framework/flask.py (depends on T015, T007)
- [x] T019 [US1] Add comprehensive error handling for Flask routes in src/novu_framework/flask.py (depends on T006, T015, T018)
- [x] T020 [US1] Document Flask example in README.md

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Compatibility with Existing Workflows (Priority: P1)

**Goal**: Ensure existing workflow definitions work unchanged with Flask integration

**Independent Test**: Use same workflow definitions as FastAPI in Flask app and verify identical execution

### Tests for User Story 2 (Constitution Mandated) ⚠️

- [ ] T021 [P] [US2] Integration test for existing workflow compatibility in tests/integration/test_flask.py
- [ ] T022 [P] [US2] Integration test for workflow step controls in tests/integration/test_flask.py
- [ ] T023 [P] [US2] Integration test for multi-step workflows in tests/integration/test_flask.py
- [ ] T024 [P] [US2] Performance test comparing Flask vs FastAPI execution in tests/integration/test_flask.py

### Implementation for User Story 2

- [ ] T025 [US2] Validate workflow registration compatibility in src/novu_framework/flask.py (depends on T016)
- [ ] T026 [US2] Ensure step control processing works identically to FastAPI in src/novu_framework/flask.py (depends on T018, T025)
- [ ] T027 [US2] Verify multi-step workflow execution order in src/novu_framework/flask.py (depends on T018, T026)
- [ ] T028 [US2] Add workflow compatibility validation in src/novu_framework/flask.py (depends on T025, T026, T027)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Error Handling and Validation (Priority: P2)

**Goal**: Provide proper error handling and validation with clear HTTP status codes

**Independent Test**: Trigger error conditions (missing workflows, invalid payloads) and verify appropriate HTTP responses

### Tests for User Story 3 (Constitution Mandated) ⚠️

- [ ] T029 [P] [US3] Unit test for 404 workflow not found errors in tests/unit/test_flask.py
- [ ] T030 [P] [US3] Unit test for 400 validation errors in tests/unit/test_flask.py
- [ ] T031 [P] [US3] Unit test for 500 internal server errors in tests/unit/test_flask.py
- [ ] T032 [P] [US3] Integration test for error response format consistency in tests/integration/test_flask.py

### Implementation for User Story 3

- [ ] T033 [US3] Implement 404 error handling for missing workflows in src/novu_framework/flask.py (depends on T015)
- [ ] T034 [US3] Implement 400 error handling for payload validation in src/novu_framework/flask.py (depends on T008, T033)
- [ ] T035 [US3] Implement 500 error handling for internal workflow errors in src/novu_framework/flask.py (depends on T018, T034)
- [ ] T036 [US3] Ensure error response format matches FastAPI exactly in src/novu_framework/flask.py (depends on T033, T034, T035)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T037 [P] Add comprehensive docstrings to Flask integration module in src/novu_framework/flask.py
- [ ] T038 [P] Create unit tests for Flask module helper functions in tests/unit/test_flask.py
- [ ] T039 [P] Add performance benchmarks for Flask integration in tests/integration/test_flask.py
- [ ] T040 Update README.md with Flask integration examples
- [ ] T041 Validate quickstart.md examples work with actual Flask implementation
- [ ] T042 Add Flask integration to package documentation
- [ ] T043 Run full test suite to ensure 100% coverage and compatibility

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 completion for workflow execution
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 completion for error handling endpoints

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Constitution: Test-First Development)
- Core endpoints before compatibility validation
- Error handling after basic functionality
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, User Story 1 and 2 can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (Constitution mandated):
Task: "Contract test for health check endpoint in tests/contract/test_api_contract.py"
Task: "Contract test for workflow execution endpoint in tests/contract/test_api_contract.py"
Task: "Integration test for Flask app setup in tests/integration/test_flask.py"
Task: "Integration test for workflow discovery in tests/integration/test_flask.py"
Task: "Integration test for workflow execution in tests/integration/test_flask.py"

# Launch implementation tasks for User Story 1:
Task: "Implement health check endpoint in src/novu_framework/flask.py"
Task: "Implement workflow execution endpoint in src/novu_framework/flask.py"
Task: "Create serve() function for Flask app integration in src/novu_framework/flask.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Flask Integration)
   - Developer B: User Story 2 (Compatibility)
   - Developer C: User Story 3 (Error Handling)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Constitution mandates Test-First Development - verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks must maintain 100% API compatibility with FastAPI integration
- Flask integration must reuse existing validation models without modification
