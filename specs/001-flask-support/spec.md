# Feature Specification: Flask Support

**Feature Branch**: `001-flask-support`
**Created**: 2026-01-24
**Status**: Draft
**Input**: User description: "add Flask support"

## Domain Alignment

**Primary Purpose**: Must directly support notification workflow patterns or enable core notification functionality
**Constitution Compliance**: Library-First Design, Pythonic Interface, Test-First Development, Minimal Dependencies

## User Scenarios & Testing _(mandatory)_

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently

  All stories must include testing requirements aligned with Constitution:
  - Unit tests for core logic (100% coverage)
  - Integration tests for workflow scenarios
  - Performance tests for high-volume scenarios
-->

### User Story 1 - Flask Integration (Priority: P1)

Developers want to use the novu-framework with Flask applications instead of FastAPI, providing the same workflow serving capabilities but compatible with Flask's ecosystem.

**Why this priority**: Flask is one of the most popular Python web frameworks, and supporting it expands the framework's adoption significantly while maintaining the same developer experience as FastAPI integration.

**Independent Test**: Can be fully tested by creating a Flask app, registering workflows, and making HTTP requests to verify workflow discovery and execution endpoints work correctly.

**Acceptance Scenarios**:

1. **Given** a Flask application is created, **When** the novu Flask serve function is called with workflows, **Then** the endpoints should be registered and accessible
2. **Given** workflows are registered with Flask, **When** a GET request is made to the health endpoint, **Then** it should return workflow discovery information
3. **Given** a workflow exists, **When** a POST request is made to execute it, **Then** the workflow should trigger and return results

---

### User Story 2 - Compatibility with Existing Workflows (Priority: P1)

Users want to use their existing workflow definitions unchanged with Flask, ensuring no code changes are required when switching between FastAPI and Flask.

**Why this priority**: Maintaining workflow compatibility ensures developers can easily switch web frameworks without refactoring their business logic, reducing migration friction.

**Independent Test**: Can be fully tested by using the same workflow definitions that work with FastAPI in a Flask application and verifying they execute identically.

**Acceptance Scenarios**:

1. **Given** existing workflow definitions, **When** they are used with Flask integration, **Then** they should work without any modifications
2. **Given** a workflow with step controls, **When** executed via Flask, **Then** the controls should be processed correctly
3. **Given** a workflow with multiple steps, **When** executed via Flask, **Then** all steps should execute in order

---

### User Story 3 - Error Handling and Validation (Priority: P2)

Developers need proper error handling and validation when using Flask integration, with clear error messages and HTTP status codes.

**Why this priority**: Good error handling is essential for debugging and production stability, matching the quality of the existing FastAPI integration.

**Independent Test**: Can be fully tested by triggering various error conditions (missing workflows, invalid payloads, etc.) and verifying appropriate HTTP responses.

**Acceptance Scenarios**:

1. **Given** a request to execute a non-existent workflow, **When** the endpoint is called, **Then** it should return a 404 error with clear message
2. **Given** invalid payload data, **When** workflow execution is attempted, **Then** it should return a 400 error with validation details
3. **Given** an internal workflow error, **When** execution fails, **Then** it should return a 500 error with error details

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- What happens when Flask app is already running with other routes?
- How does system handle concurrent workflow executions in Flask?
- What happens when Flask app context is not available?

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST provide a Flask integration module equivalent to FastAPI integration
- **FR-002**: System MUST support the same workflow registration API as FastAPI version
- **FR-003**: System MUST provide health check endpoint for workflow discovery
- **FR-004**: System MUST provide workflow execution endpoint with same payload structure
- **FR-005**: System MUST maintain compatibility with existing workflow definitions
- **FR-006**: System MUST provide proper HTTP status codes and error responses
- **FR-007**: System MUST support async workflow execution within Flask's sync context
- **FR-008**: System MUST handle Flask's request/response patterns correctly

### Key Entities _(include if feature involves data)_

- **Flask Integration Module**: Provides Flask-specific workflow serving functionality
- **Workflow Registry**: Maps workflow IDs to workflow objects within Flask context
- **HTTP Endpoints**: Flask routes for health check and workflow execution
- **Error Handlers**: Flask-specific error response formatting

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Developer can integrate novu-framework with Flask in under 5 minutes
- **SC-002**: Flask integration provides 100% API compatibility with FastAPI version
- **SC-003**: All existing workflow tests pass without modification when using Flask
- **SC-004**: Flask integration maintains same performance characteristics as FastAPI (within 10%)
- **SC-005**: Error responses are consistent and properly formatted across both frameworks
