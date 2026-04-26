## ADDED Requirements

### Requirement: Familiar project structure
The system SHALL use a simplified project structure inspired by `demo/kraits-core-service`.

#### Scenario: Runtime wiring is in infrastructure
- **WHEN** a developer opens the project
- **THEN** FastAPI startup, settings, logging, middleware, database configuration, and API router wiring are under `infrastructure/`

#### Scenario: Domain code is in app core
- **WHEN** a developer opens the project
- **THEN** request/response schemas and business services are under `app/core/`

#### Scenario: Persistence code is in data
- **WHEN** a developer opens the project
- **THEN** SQLAlchemy models and repository functions are under `data/`

### Requirement: Simple controller service repository flow
The system SHALL organize API behavior as controller -> service -> repository where useful.

#### Scenario: Transaction request flow
- **WHEN** a transaction endpoint handles a request
- **THEN** the controller delegates business behavior to a service and database behavior to a repository

#### Scenario: No RBAC layers are required
- **WHEN** a route is defined
- **THEN** it does not require JWT auth, RBAC middleware, route interceptors, or permission decorators

### Requirement: Request ID logging
The system SHALL include simple request-id-aware console logging.

#### Scenario: API request is handled
- **WHEN** the API handles an HTTP request
- **THEN** logs emitted during that request can include a request ID

#### Scenario: Response contains request ID
- **WHEN** the API returns a response
- **THEN** the response includes an `X-Request-ID` header

### Requirement: VS Code debug configuration
The system SHALL include a VS Code launch configuration for debugging the FastAPI app.

#### Scenario: Debug profile exists
- **WHEN** a developer opens `.vscode/launch.json`
- **THEN** it includes a FastAPI uvicorn launch profile targeting `infrastructure.main:app`

#### Scenario: Debug profile uses local environment
- **WHEN** the debug profile starts
- **THEN** it loads `.env`, sets `PYTHONPATH` to the workspace, enables reload, and runs on port `8000`
