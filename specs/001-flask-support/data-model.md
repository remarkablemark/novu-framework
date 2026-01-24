# Data Model: Flask Support

**Date**: 2026-01-24
**Feature**: Flask Support for novu-framework

## Overview

The Flask integration does not introduce new data entities but leverages existing validation models and workflow structures. This document outlines the data flow and relationships specific to Flask integration.

## Existing Data Models (Reused)

### Workflow

- **Source**: `src/novu_framework/workflow.py`
- **Purpose**: Core workflow definition and execution logic
- **Fields**: workflow_id, handler function, step definitions
- **Validation**: No modifications required

### Validation Models

- **Source**: `src/novu_framework/validation/api.py`
- **Purpose**: Request/response validation models
- **Models**:
  - `HealthCheckResponse`: Health check endpoint response
  - `TriggerPayload`: Workflow execution request payload
  - `Discovered`: Workflow and step discovery information

## Flask-Specific Data Flow

### Request Processing

```python
# HTTP Request → Flask Route → Validation → Workflow Execution → Response
Flask Request → Pydantic Model → Workflow.trigger() → JSON Response
```

### Workflow Registry

- **Type**: `Dict[str, Workflow]`
- **Purpose**: Maps workflow IDs to workflow objects
- **Scope**: Flask application context
- **Lifetime**: Application lifecycle

### Error Data

- **Type**: JSON error responses
- **Structure**: Matches FastAPI error format
- **Fields**: detail, status_code, error_type

## State Management

### Stateless Design

- No persistent state in Flask integration
- Workflow state managed by core workflow engine
- HTTP requests are independent

### Flask Context

- Workflow registry stored in Flask app config
- No Flask session or request context dependencies
- Async execution handled outside Flask request context

## Data Validation

### Input Validation

- Reuses existing Pydantic models
- Same validation rules as FastAPI integration
- Automatic JSON deserialization and validation

### Output Validation

- Workflow results serialized to JSON
- Response format matches FastAPI integration
- Error responses follow consistent structure

## Performance Considerations

### Memory Usage

- Workflow registry: O(n) where n = number of workflows
- Request processing: O(1) additional overhead
- No per-request state accumulation

### Data Transfer

- JSON serialization/deserialization
- Minimal data transformation overhead
- Direct pass-through to workflow engine

## Security Considerations

### Input Sanitization

- Pydantic model validation prevents injection
- JSON parsing limits prevent DoS
- No raw data processing

### Error Information

- Sanitized error messages
- No internal state exposure
- Consistent error format prevents information leakage

## Integration Points

### Core Workflow Engine

- **Interface**: Existing workflow.trigger() method
- **Data Flow**: Payload → Workflow → Result
- **Compatibility**: 100% with existing workflows

### Validation Layer

- **Interface**: Pydantic models
- **Data Flow**: Request → Model → Validated Data
- **Compatibility**: Identical to FastAPI integration

### HTTP Layer

- **Interface**: Flask routes and error handlers
- **Data Flow**: HTTP → JSON → Model → Workflow → JSON → HTTP
- **Compatibility**: Same API contract as FastAPI

## Testing Data Requirements

### Unit Tests

- Mock workflow objects
- Sample validation payloads
- Error scenario data

### Integration Tests

- Real workflow definitions
- HTTP request/response examples
- Performance benchmark data

### Contract Tests

- API compatibility data
- Error response format validation
- Cross-framework consistency checks

## Conclusion

The Flask integration reuses all existing data models without modification, ensuring complete compatibility with the FastAPI integration. The data flow remains identical, with Flask serving as a thin HTTP layer that preserves the same validation, execution, and response patterns.
