# Data Model: GET Request Handler

**Feature**: GET Request Handler | **Date**: 2025-01-24 | **Phase**: 1

## Core Entities

### GetActionEnum

Enumeration of supported GET actions, matching Novu framework pattern.

```python
from enum import Enum

class GetActionEnum(str, Enum):
    DISCOVER = "discover"
    HEALTH_CHECK = "health-check"
    CODE = "code"
```

**Fields**:

- `DISCOVER`: Returns workflow discovery information
- `HEALTH_CHECK`: Returns system health status
- `CODE`: Returns code-related information

**Validation Rules**:

- Must be one of the three defined enum values
- Case-sensitive matching

### GetRequestQuery

Query parameters for GET requests.

```python
from pydantic import BaseModel, Field
from typing import Optional

class GetRequestQuery(BaseModel):
    action: GetActionEnum = Field(
        default=GetActionEnum.HEALTH_CHECK,
        description="Action to perform"
    )
    workflow_id: Optional[str] = Field(
        default=None,
        description="Workflow ID (required for code action)"
    )
    step_id: Optional[str] = Field(
        default=None,
        description="Step ID (required for code action)"
    )
```

**Fields**:

- `action`: Required action enum (defaults to health-check)
- `workflow_id`: Optional workflow identifier
- `step_id`: Optional step identifier

**Validation Rules**:

- `action` must be valid GetActionEnum value
- `workflow_id` and `step_id` required when action is `code`
- `workflow_id` and `step_id` ignored for other actions

### DiscoverResponse

Response for discover action containing workflow information, matching Novu cloud format.

```python
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class JSONSchema(BaseModel):
    """JSON Schema definition for validation"""
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)
    additionalProperties: bool = True

class StepControls(BaseModel):
    schema: JSONSchema
    unknownSchema: Dict[str, Any] = Field(default_factory=dict)

class StepOutputs(BaseModel):
    schema: JSONSchema
    unknownSchema: Dict[str, Any] = Field(default_factory=dict)

class StepResults(BaseModel):
    schema: JSONSchema
    unknownSchema: Dict[str, Any] = Field(default_factory=dict)

class WorkflowStep(BaseModel):
    step_id: str = Field(description="Step identifier")
    type: str = Field(description="Step type (in_app, chat, email, sms, push)")
    controls: StepControls = Field(description="Step input controls and validation")
    outputs: StepOutputs = Field(description="Step output schema")
    results: Optional[StepResults] = Field(default=None, description="Step results schema")
    code: str = Field(description="Step implementation code")
    options: Dict[str, Any] = Field(default_factory=dict, description="Step options")
    providers: List[str] = Field(default_factory=list, description="Available providers")

class WorkflowPayload(BaseModel):
    schema: JSONSchema
    unknownSchema: Dict[str, Any] = Field(default_factory=dict)

class WorkflowControls(BaseModel):
    schema: JSONSchema
    unknownSchema: Dict[str, Any] = Field(default_factory=dict)

class WorkflowDetail(BaseModel):
    workflow_id: str = Field(description="Workflow identifier")
    severity: str = Field(default="none", description="Workflow severity level")
    steps: List[WorkflowStep] = Field(description="List of workflow steps")
    code: str = Field(description="Workflow implementation code")
    payload: WorkflowPayload = Field(description="Workflow payload schema")
    controls: WorkflowControls = Field(description="Workflow controls schema")

class DiscoverResponse(BaseModel):
    workflows: List[WorkflowDetail] = Field(description="List of discovered workflows")
```

**Fields**:

- `workflows`: Detailed list of all discovered workflows

### DiscoveredWorkflows

Legacy discovery metrics for health check compatibility.

```python
class DiscoveredWorkflows(BaseModel):
    workflows: int = Field(description="Number of discovered workflows")
    steps: int = Field(description="Total number of steps across all workflows")
```

**Fields**:

- `workflows`: Number of discovered workflows
- `steps`: Total number of steps across all workflows

### HealthCheckResponse

Response for health-check action containing system status, matching original format.

```python
class HealthCheckResponse(BaseModel):
    status: str = Field(description="System health status")
    sdk_version: str = Field(description="SDK version")
    framework_version: str = Field(description="Framework version")
    discovered: DiscoveredWorkflows = Field(description="Workflow discovery metrics")
```

**Fields**:

- `status`: Health status (ok/unhealthy)
- `sdk_version`: SDK version string
- `framework_version`: Framework version string
- `discovered`: Current workflow discovery metrics

### CodeResponse

Response for code action containing workflow implementation code.

```python
class CodeResponse(BaseModel):
    code: str = Field(description="Workflow implementation code")
```

**Fields**:

- `code`: Complete workflow implementation code

## Entity Relationships

```
GetRequestQuery
  ├── action → GetActionEnum
  ├── workflow_id (optional, required for CODE)
  └── step_id (optional, required for CODE)

JSONSchema
  ├── type
  ├── properties
  ├── required
  └── additionalProperties

StepControls
  ├── schema → JSONSchema
  └── unknownSchema

StepOutputs
  ├── schema → JSONSchema
  └── unknownSchema

StepResults
  ├── schema → JSONSchema
  └── unknownSchema

WorkflowStep
  ├── step_id
  ├── type
  ├── controls → StepControls
  ├── outputs → StepOutputs
  ├── results → StepResults (optional)
  ├── code
  ├── options
  └── providers

WorkflowPayload
  ├── schema → JSONSchema
  └── unknownSchema

WorkflowControls
  ├── schema → JSONSchema
  └── unknownSchema

WorkflowDetail
  ├── workflow_id
  ├── severity
  ├── steps → List[WorkflowStep]
  ├── code
  ├── payload → WorkflowPayload
  ├── controls → WorkflowControls
  ├── tags
  └── preferences

DiscoverResponse
  └── workflows → List[WorkflowDetail]

DiscoveredWorkflows
  ├── workflows
  └── steps

HealthCheckResponse
  ├── status
  ├── sdk_version
  ├── framework_version
  └── discovered → DiscoveredWorkflows

CodeResponse
  └── code
```

## State Transitions

### Request Processing Flow

1. **Query Validation**: Parse and validate query parameters
2. **Action Routing**: Route to appropriate handler based on action
3. **Response Generation**: Generate appropriate response model
4. **Error Handling**: Return error responses for invalid requests

### Action-Specific Flows

#### Discover Action

```
GET /?action=discover
↓
Validate query parameters
↓
Scan registered workflows
↓
Count steps and workflows
↓
Return DiscoverResponse
```

#### Health Check Action

```
GET /?action=health-check
↓
Validate query parameters
↓
Check system status
↓
Get workflow counts
↓
Return HealthCheckResponse
```

#### Code Action

```
GET /?action=code&workflow_id={id}&step_id={id}
↓
Validate query parameters (workflow_id and step_id required)
↓
Lookup workflow and step
↓
Extract code/metadata
↓
Return CodeResponse
```

## Data Validation Rules

### Input Validation

- Action must be valid enum value
- Code action requires both workflow_id and step_id
- Query parameters must be properly URL-encoded

### Output Validation

- All responses must be valid JSON
- Required fields must be present
- Optional fields must have proper defaults

### Error Conditions

- Invalid action parameter → 400 Bad Request
- Missing workflow_id/step_id for code action → 400 Bad Request
- Workflow not found → 404 Not Found
- Step not found → 404 Not Found
