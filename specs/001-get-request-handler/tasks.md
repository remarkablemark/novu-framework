# Implementation Tasks: GET Request Handler

**Feature**: GET Request Handler | **Date**: 2025-01-24 | **Branch**: `001-get-request-handler`
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md) | **Data Model**: [data-model.md](data-model.md)
**Contracts**: [contracts/](contracts/) | **Quickstart**: [quickstart.md](quickstart.md)

## Summary

Add GET request handling to the Novu Python framework to support three actions (discover, health-check, code) via query parameters. This implementation extends existing FastAPI and Flask integrations while maintaining backward compatibility with POST endpoints.

**Total Tasks**: 23
**Stories**: 3 (P1: Health Check, P2: Webhook Validation, P3: CORS Support)
**Parallel Opportunities**: 8 tasks can be parallelized

## Phase 1: Setup

### Goal

Prepare project structure and foundation for GET request implementation.

### Independent Test Criteria

- Project structure is ready for implementation
- All required dependencies are available
- Development environment is configured

### Tasks

- [ ] T001 Create feature branch `001-get-request-handler` from main
- [ ] T002 Verify existing FastAPI and Flask integration modules are accessible
- [ ] T003 Confirm Pydantic models and validation patterns are available
- [ ] T004 Set up test structure for GET endpoint testing
- [ ] T005 Review existing error handling patterns in POST endpoints

## Phase 2: Foundational

### Goal

Implement core infrastructure and shared components needed by all user stories.

### Independent Test Criteria

- GetActionEnum is defined and testable
- Query validation models are implemented
- Response models are defined and serializable
- Error handling is consistent with existing patterns

### Tasks

- [ ] T006 Add GetActionEnum to src/novu_framework/constants.py
- [ ] T007 Create GetRequestQuery model in src/novu_framework/validation/api.py
- [ ] T008 [P] Create JSONSchema model in src/novu_framework/validation/api.py
- [ ] T009 [P] Create StepControls model in src/novu_framework/validation/api.py
- [ ] T010 [P] Create StepOutputs model in src/novu_framework/validation/api.py
- [ ] T011 [P] Create StepResults model in src/novu_framework/validation/api.py
- [ ] T012 [P] Create WorkflowStep model in src/novu_framework/validation/api.py
- [ ] T013 [P] Create WorkflowPayload model in src/novu_framework/validation/api.py
- [ ] T014 [P] Create WorkflowControls model in src/novu_framework/validation/api.py
- [ ] T015 [P] Create WorkflowDetail model in src/novu_framework/validation/api.py
- [ ] T016 [P] Create DiscoverResponse model in src/novu_framework/validation/api.py
- [ ] T017 [P] Create DiscoveredWorkflows model in src/novu_framework/validation/api.py
- [ ] T018 [P] Create HealthCheckResponse model in src/novu_framework/validation/api.py
- [ ] T019 [P] Create CodeResponse model in src/novu_framework/validation/api.py
- [ ] T020 Implement GET action routing logic in src/novu_framework/fastapi.py
- [ ] T021 [P] Implement GET action routing logic in src/novu_framework/flask.py

## Phase 3: User Story 1 - Bridge Health Check (P1)

### Goal

Enable developers to verify bridge endpoint accessibility and health status.

### Independent Test Criteria

- GET `?action=health-check` returns proper health status
- Response includes workflow discovery metrics
- Response time is under 100ms
- Authentication works consistently with POST endpoints

### Tasks

- [ ] T022 [US1] Implement health check handler in src/novu_framework/fastapi.py
- [ ] T023 [P] [US1] Implement health check handler in src/novu_framework/flask.py
- [ ] T024 [US1] Add workflow discovery counting logic to health check
- [ ] T025 [US1] Add unit tests for health check action in tests/unit/test_fastapi.py
- [ ] T026 [P] [US1] Add unit tests for health check action in tests/unit/test_flask.py
- [ ] T027 [US1] Add integration tests for health check endpoint in tests/integration/test_fastapi.py
- [ ] T028 [P] [US1] Add integration tests for health check endpoint in tests/integration/test_flask.py

## Phase 4: User Story 2 - Webhook Validation (P2)

### Goal

Enable Novu cloud service to validate webhook endpoint accessibility.

### Independent Test Criteria

- GET `?action=discover` returns workflow discovery information
- Response matches Novu cloud format exactly
- Complex workflow schemas are properly serialized
- Authentication validation works for discover requests

### Tasks

- [ ] T029 [US2] Implement discover handler in src/novu_framework/fastapi.py
- [ ] T030 [P] [US2] Implement discover handler in src/novu_framework/flask.py
- [ ] T031 [US2] Add workflow schema extraction logic for discover response
- [ ] T032 [US2] Add unit tests for discover action in tests/unit/test_fastapi.py
- [ ] T033 [P] [US2] Add unit tests for discover action in tests/unit/test_flask.py
- [ ] T034 [US2] Add integration tests for discover endpoint in tests/integration/test_fastapi.py
- [ ] T035 [P] [US2] Add integration tests for discover endpoint in tests/integration/test_flask.py

## Phase 5: User Story 3 - CORS Preflight Support (P3)

### Goal

Enable browser-based applications to make cross-origin requests to bridge endpoints.

### Independent Test Criteria

- OPTIONS requests return proper CORS headers
- Cross-origin GET requests include CORS headers
- Error responses include CORS headers
- CORS configuration is customizable

### Tasks

- [ ] T036 [US3] Add OPTIONS handler for CORS preflight in src/novu_framework/fastapi.py
- [ ] T037 [P] [US3] Add OPTIONS handler for CORS preflight in src/novu_framework/flask.py
- [ ] T038 [US3] Implement CORS middleware configuration
- [ ] T039 [US3] Add unit tests for CORS handling in tests/unit/test_fastapi.py
- [ ] T040 [P] [US3] Add unit tests for CORS handling in tests/unit/test_flask.py
- [ ] T041 [US3] Add integration tests for CORS in tests/integration/test_fastapi.py
- [ ] T042 [P] [US3] Add integration tests for CORS in tests/integration/test_flask.py

## Phase 6: Code Action Implementation

### Goal

Enable retrieval of workflow implementation code for development and debugging.

### Independent Test Criteria

- GET `?action=code&workflowId={id}` returns workflow code
- Invalid workflow IDs return proper error responses
- Code response matches Novu cloud format
- Authentication validation works for code requests

### Tasks

- [ ] T043 Implement code handler in src/novu_framework/fastapi.py
- [ ] T044 [P] Implement code handler in src/novu_framework/flask.py
- [ ] T045 Add workflow code extraction logic
- [ ] T046 Add unit tests for code action in tests/unit/test_fastapi.py
- [ ] T047 [P] Add unit tests for code action in tests/unit/test_flask.py
- [ ] T048 Add integration tests for code endpoint in tests/integration/test_fastapi.py
- [ ] T049 [P] Add integration tests for code endpoint in tests/integration/test_flask.py

## Phase 7: Polish & Cross-Cutting Concerns

### Goal

Complete implementation with error handling, logging, and documentation.

### Independent Test Criteria

- All error responses are consistent and properly formatted
- GET request handling is logged for debugging
- Performance requirements are met
- Documentation is complete and accurate

### Tasks

- [ ] T050 Implement consistent error handling for GET endpoints
- [ ] T051 Add logging for GET request handling
- [ ] T052 Add performance optimization for health check and discover
- [ ] T053 Update API documentation with GET endpoint examples
- [ ] T054 Add contract tests for OpenAPI specification compliance
- [ ] T055 Add performance tests for GET endpoints
- [ ] T056 Update quickstart guide with complete usage examples

## Dependencies

### Story Completion Order

1. **Phase 1 & 2** (Setup & Foundational) - Must complete first
2. **User Story 1** (Health Check) - Can be implemented independently after foundations
3. **User Story 2** (Webhook Validation) - Can be implemented in parallel with US1
4. **User Story 3** (CORS Support) - Can be implemented in parallel with US1 & US2
5. **Code Action** - Depends on workflow registry from US2
6. **Phase 7** (Polish) - Final phase after all stories complete

### Critical Dependencies

- T020-T021 (Routing logic) must complete before any story implementation
- T022-T028 (Health Check) must complete before performance optimization
- T029-T035 (Discover) must complete before code action implementation
- All story phases must complete before polish phase

## Parallel Execution Examples

### Within User Story 1 (Health Check)

```bash
# Parallel execution of FastAPI and Flask implementations
T022 & T023  # Health check handlers
T025 & T026  # Unit tests
T027 & T028  # Integration tests
```

### Within User Story 2 (Webhook Validation)

```bash
# Parallel execution of FastAPI and Flask implementations
T029 & T030  # Discover handlers
T032 & T033  # Unit tests
T034 & T035  # Integration tests
```

### Within User Story 3 (CORS Support)

```bash
# Parallel execution of FastAPI and Flask implementations
T036 & T037  # CORS handlers
T039 & T040  # Unit tests
T041 & T042  # Integration tests
```

### Within Code Action Implementation

```bash
# Parallel execution of FastAPI and Flask implementations
T043 & T044  # Code handlers
T046 & T047  # Unit tests
T048 & T049  # Integration tests
```

## Implementation Strategy

### MVP Scope (First Release)

Focus on User Story 1 (Health Check) for immediate value:

- Tasks T001-T028 (Setup, Foundational, Health Check)
- Provides basic bridge endpoint validation
- Enables production deployment verification

### Incremental Delivery

1. **Sprint 1**: Health Check (T001-T028)
2. **Sprint 2**: Webhook Validation (T029-T035)
3. **Sprint 3**: CORS Support (T036-T042)
4. **Sprint 4**: Code Action & Polish (T043-T056)

### Risk Mitigation

- Implement FastAPI version first, then Flask (parallelizable)
- Use existing POST endpoint patterns for consistency
- Leverage existing authentication and error handling
- Comprehensive testing at each phase

## Success Criteria

### Technical Success

- All GET endpoints return responses matching Novu cloud format
- Response times under 100ms for health check and discover
- 100% backward compatibility with existing POST endpoints
- Test coverage > 90% for new functionality

### User Success

- Developers can verify bridge health with simple GET request
- Novu cloud can validate webhooks without errors
- Browser applications can access bridge endpoints
- Complete workflow discovery and code retrieval functionality

---

**Next Steps**: Begin with Phase 1 setup tasks, proceeding through phases in dependency order. Each phase should be completed and tested before moving to the next phase.
