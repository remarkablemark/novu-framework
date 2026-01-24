# Research: Flask Support

**Date**: 2026-01-24
**Feature**: Flask Support for novu-framework

## Research Summary

This research addresses the technical considerations for adding Flask web framework support to the novu-framework while maintaining compatibility with the existing FastAPI integration.

## Key Research Areas

### 1. Flask Async Support

**Decision**: Use Flask's built-in async route support with `async def` handlers

**Rationale**:

- Flask 2.0+ supports async routes natively
- Allows seamless integration with existing async workflow execution
- Maintains consistency with FastAPI's async patterns

**Alternatives considered**:

- Synchronous wrappers around async workflows (rejected: adds complexity and performance overhead)
- Separate sync/Flask-specific workflow execution (rejected: code duplication)

### 2. Flask Integration Pattern

**Decision**: Mirror FastAPI integration structure with Flask Blueprint

**Rationale**:

- Consistent API surface across frameworks
- Reuses existing validation models and workflow logic
- Flask Blueprint equivalent to FastAPI Router

**Alternatives considered**:

- Completely different Flask-specific API (rejected: breaks compatibility goal)
- Decorator-based route registration (rejected: less flexible than Blueprint approach)

### 3. Error Handling Strategy

**Decision**: Use Flask's error handlers with JSON responses matching FastAPI format

**Rationale**:

- Maintains API compatibility between frameworks
- Provides consistent error response structure
- Leverages Flask's built-in error handling mechanisms

**Alternatives considered**:

- Flask-specific error formats (rejected: breaks compatibility)
- Manual error handling in each route (rejected: code duplication)

### 4. Testing Approach

**Decision**: Use Flask's test client with pytest, following existing test patterns

**Rationale**:

- Flask's test client provides equivalent functionality to FastAPI TestClient
- Allows reuse of existing test patterns and assertions
- Maintains test consistency across framework integrations

**Alternatives considered**:

- Manual HTTP requests (rejected: more complex and less reliable)
- Separate testing framework (rejected: adds unnecessary dependency)

### 5. Dependency Management

**Decision**: Add Flask as optional dependency with extras

**Rationale**:

- Keeps core framework minimal
- Allows users to choose their web framework
- Follows Python packaging best practices

**Alternatives considered**:

- Required Flask dependency (rejected: breaks minimal dependency principle)
- Separate Flask package (rejected: over-engineering for this use case)

## Technical Decisions

### Flask Module Structure

```python
# src/novu_framework/flask.py
from flask import Blueprint, request, jsonify
from typing import List, Dict, Any

def serve(app: Flask, route: str = "/api/novu", workflows: List[Workflow] = []) -> None:
    """Serve Novu workflows via Flask."""
    # Implementation mirroring FastAPI pattern
```

### Route Registration

- Use Flask Blueprint for route organization
- Same endpoint paths as FastAPI integration
- Identical request/response formats

### Async Execution

- Use Flask's async route support
- Leverage existing async workflow execution
- Handle async/sync context properly

### Error Responses

- JSON responses matching FastAPI format
- Proper HTTP status codes
- Consistent error message structure

## Implementation Considerations

### Performance

- Flask performance should be comparable to FastAPI for this use case
- Async execution prevents blocking
- Minimal overhead from Flask layer

### Compatibility

- 100% API compatibility with FastAPI integration
- Existing workflows work without modification
- Same validation models and error handling

### Dependencies

- Flask as optional dependency
- No additional core dependencies required
- Maintains minimal dependency footprint

## Conclusion

The research confirms that Flask integration is feasible while maintaining all constitutional requirements. The approach mirrors the existing FastAPI integration patterns, ensuring consistency and compatibility. Flask's native async support and Blueprint system provide the necessary tools for equivalent functionality.
