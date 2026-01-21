# Feature Specification: Python Framework Package

**Feature Branch**: `001-python-framework`
**Created**: 2026-01-20
**Status**: Draft
**Input**: User description: "Create a Python package that emulates npm TypeScript package https://github.com/novuhq/novu/tree/v3.12.0/packages/framework"

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

### User Story 1 - Basic Workflow Definition (Priority: P1)

As a Python developer, I want to define notification workflows using Python decorators and functions so that I can create code-first notification workflows similar to the TypeScript @novu/framework.

**Why this priority**: This is the core functionality that enables users to define workflows, which is the primary purpose of the framework.

**Independent Test**: Can be fully tested by creating a simple workflow with a single step and verifying it can be triggered programmatically.

**Acceptance Scenarios**:

1. **Given** a Python workflow function with @workflow decorator, **When** the function is defined, **Then** it should be registered as a valid workflow
2. **Given** a registered workflow, **When** trigger() is called with valid payload, **Then** the workflow should execute successfully

---

### User Story 2 - Multi-Step Workflows (Priority: P1)

As a Python developer, I want to create workflows with multiple steps (in_app, digest, email) so that I can build complex notification sequences.

**Why this priority**: Multi-step workflows are essential for real-world notification scenarios and differentiate the framework from simple notification senders.

**Independent Test**: Can be fully tested by creating a workflow with in_app, digest, and email steps and verifying step execution order and data flow.

**Acceptance Scenarios**:

1. **Given** a workflow with multiple steps, **When** triggered, **Then** steps should execute in the defined order
2. **Given** a digest step with cron expression, **When** multiple events accumulate, **Then** digest should batch events according to schedule

---

### User Story 3 - Framework Integration (Priority: P2)

As a Python developer, I want to integrate the framework with popular Python web frameworks (FastAPI, Flask, Django) so that I can serve workflows via HTTP endpoints.

**Why this priority**: Framework integration enables real-world usage and allows workflows to be triggered by external systems.

**Independent Test**: Can be fully tested by creating a FastAPI application that serves workflows and verifying HTTP endpoints are properly registered.

**Acceptance Scenarios**:

1. **Given** a FastAPI application with novu workflows, **When** the app starts, **Then** workflow endpoints should be available
2. **Given** an HTTP request to workflow endpoint, **When** valid payload is received, **Then** workflow should trigger and return appropriate response

---

### Edge Cases

- What happens when workflow payload validation fails?
- How does system handle step execution failures and retries?
- What happens when digest schedule expressions are invalid?
- How does system handle concurrent workflow triggers?
- What happens when external dependencies (email providers) are unavailable?

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST provide a @workflow decorator for defining notification workflows
- **FR-002**: System MUST support step functions (in_app, digest, email, sms, push) within workflows
- **FR-003**: System MUST validate workflow payloads using Python type hints or schema validation
- **FR-004**: System MUST support cron expressions for digest scheduling
- **FR-005**: System MUST provide workflow.trigger() method for manual execution
- **FR-006**: System MUST integrate with FastAPI framework via serve() function
- **FR-007**: System MUST support workflow step skipping based on conditions
- **FR-008**: System MUST provide control schema validation for non-technical stakeholders
- **FR-009**: System MUST handle async workflow execution
- **FR-010**: System MUST maintain workflow execution state and history

### Key Entities

- **Workflow**: Represents a notification workflow with steps, payload schema, and execution logic
- **Step**: Represents individual notification actions (in_app, digest, email, sms, push) within a workflow
- **Payload**: Data structure passed to workflow triggers, validated against schema
- **Digest**: Time-based batching mechanism for accumulating multiple events before processing
- **Control Schema**: Validation schema for non-technical configuration modifications
- **Execution Context**: Runtime state and data passed between workflow steps

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Python developers can define and execute a basic workflow in under 5 minutes
- **SC-002**: System handles 1000 concurrent workflow triggers without performance degradation
- **SC-003**: 95% of workflow definitions pass validation on first attempt
- **SC-004**: Framework integration with FastAPI adds less than 50ms to request latency
- **SC-005**: Digest batching reduces individual notification volume by 80% for high-frequency events
