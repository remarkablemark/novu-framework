# Data Model: Python Framework Package

**Purpose**: Define core entities and their relationships for the notification workflow framework
**Date**: 2026-01-20
**Status**: Draft

## Core Entities

### Workflow

**Description**: Represents a notification workflow with steps, payload schema, and execution logic

**Fields**:

- `workflow_id`: str - Unique identifier for the workflow
- `name`: str - Human-readable workflow name
- `payload_schema`: Dict[str, Any] - Pydantic schema for payload validation
- `steps`: List[Step] - Ordered list of workflow steps
- `metadata`: Dict[str, Any] - Additional workflow metadata

**Validation Rules**:

- `workflow_id` must be unique within the system
- `payload_schema` must be valid Pydantic model
- At least one step must be defined
- Step names must be unique within workflow

**State Transitions**:

- `draft` → `active` → `archived`
- Cannot execute workflows in `draft` state

### Step

**Description**: Represents individual notification actions within a workflow

**Fields**:

- `step_id`: str - Unique identifier within workflow
- `step_type`: StepType - Enum (IN_APP, EMAIL, SMS, PUSH)
- `name`: str - Human-readable step name
- `config`: Dict[str, Any] - Step-specific configuration
- `skip_condition`: Optional[str] - Python expression for conditional skipping
- `control_schema`: Optional[Dict[str, Any]] - Schema for non-technical configuration

**Validation Rules**:

- `step_id` must be unique within workflow
- `step_type` must be valid enum value
- `config` must match step type requirements
- `skip_condition` must be valid Python expression if provided

**State Transitions**:

- `pending` → `executing` → `completed` → `failed`
- Steps can be retried from `failed` state

### Payload

**Description**: Data structure passed to workflow triggers, validated against schema

**Fields**:

- `workflow_id`: str - Target workflow identifier
- `recipient`: str - Target recipient identifier
- `data`: Dict[str, Any] - Payload data matching workflow schema
- `metadata`: Dict[str, Any] - Additional payload metadata

**Validation Rules**:

- `workflow_id` must reference existing active workflow
- `recipient` must be non-empty string
- `data` must validate against workflow's payload_schema

### Execution Context

**Description**: Runtime state and data passed between workflow steps

**Fields**:

- `execution_id`: str - Unique execution identifier
- `workflow_id`: str - Workflow being executed
- `payload`: Payload - Original payload data
- `step_results`: Dict[str, Any] - Results from completed steps
- `current_step`: Optional[str] - Currently executing step
- `status`: ExecutionStatus - Enum (PENDING, RUNNING, COMPLETED, FAILED)
- `started_at`: datetime - Execution start timestamp
- `completed_at`: Optional[datetime] - Execution completion timestamp

**Validation Rules**:

- `execution_id` must be unique system-wide
- `step_results` keys must match workflow step IDs
- Cannot modify `step_results` after completion

**State Transitions**:

- `PENDING` → `RUNNING` → `COMPLETED`/`FAILED`
- Failed executions can be retried, returning to `PENDING`

### Control Schema

**Description**: Validation schema for non-technical configuration modifications

**Fields**:

- `schema_id`: str - Unique schema identifier
- `workflow_id`: str - Parent workflow identifier
- `step_id`: Optional[str] - Parent step identifier (workflow-level if None)
- `schema_dict`: Dict[str, Any] - Pydantic schema definition
- `description`: str - Human-readable schema description

**Validation Rules**:

- `schema_dict` must be valid Pydantic model schema
- Only one schema per workflow/step combination
- Schema must be serializable to JSON

## Entity Relationships

```
Workflow (1) -----> (N) Step
    |
    +-----> (1) Payload Schema
    |
    +-----> (N) Control Schema

Payload (1) -----> (1) Execution Context

Execution Context (1) -----> (1) Workflow
Execution Context (1) -----> (1) Payload
```

## Data Flow

1. **Workflow Definition**: Create workflow with steps and schemas
2. **Payload Validation**: Validate incoming payload against workflow schema
3. **Execution Context**: Create context for workflow execution
4. **Step Execution**: Execute steps in order, storing results in context
5. **Result Processing**: Process completed workflows

## Performance Considerations

- **Schema Validation**: Pydantic for fast validation and type safety

## Security Considerations

- **Payload Validation**: Strict schema validation prevents injection attacks
- **Skip Conditions**: Evaluated in restricted environment
- **Control Schema**: Non-technical users can only modify approved fields
- **Execution Isolation**: Each workflow execution runs in isolated context
