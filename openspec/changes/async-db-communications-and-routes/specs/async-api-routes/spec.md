## ADDED Requirements

### Requirement: Route handlers are asynchronous
The system SHALL declare every FastAPI route handler as an asynchronous callable, including health, transaction, CSV upload, and analytics routes.

#### Scenario: Inspecting application routes
- **WHEN** the FastAPI application routes are inspected
- **THEN** every application endpoint handler is an async coroutine function

#### Scenario: Handling supported API requests
- **WHEN** a client calls any supported API endpoint
- **THEN** the endpoint executes through an async route handler without delegating blocking route work to a synchronous handler

### Requirement: Route behavior remains compatible
The system SHALL preserve the existing public HTTP API paths, request payloads, query parameters, status codes, response shapes, and validation behavior while converting routes to async execution.

#### Scenario: Existing transaction APIs are called
- **WHEN** clients call transaction creation, bulk ingestion, CSV upload, or filtered transaction listing endpoints
- **THEN** responses match the existing API contract except for implementation-level async execution

#### Scenario: Existing analytics APIs are called
- **WHEN** clients call total-sales or top-properties analytics endpoints
- **THEN** responses match the existing API contract except for implementation-level async execution

### Requirement: Route handlers await downstream async work
The system SHALL await asynchronous service and file operations from route handlers instead of returning unresolved awaitables or calling synchronous database-facing functions.

#### Scenario: Uploading a CSV file
- **WHEN** a client uploads a CSV file
- **THEN** the route awaits file reading and awaits the async transaction-ingestion service before returning a response

#### Scenario: Calling database-backed routes
- **WHEN** a client calls a database-backed route
- **THEN** the route awaits the async service operation that performs the database interaction
