## ADDED Requirements

### Requirement: Docker image build
The system SHALL include a Dockerfile that builds the FastAPI service image using the assignment command.

#### Scenario: Required Docker build command
- **WHEN** a user runs `docker build -t fastapi-app .` from the repository root
- **THEN** Docker builds an image named `fastapi-app` without requiring additional command arguments

### Requirement: Docker Compose runtime
The system SHALL include a Docker Compose setup for running the API with PostgreSQL.

#### Scenario: Compose starts API and PostgreSQL
- **WHEN** a user runs the documented Docker Compose command
- **THEN** Docker starts the FastAPI service and a PostgreSQL container

#### Scenario: PostgreSQL data is persisted
- **WHEN** the PostgreSQL container is recreated
- **THEN** transaction data remains available through a named Docker volume unless that volume is removed

### Requirement: Docker container runtime
The system SHALL run the FastAPI service inside a container on port `8000`.

#### Scenario: API binds to container network interface
- **WHEN** the API server starts inside Docker
- **THEN** it listens on `0.0.0.0:8000`

#### Scenario: API image can run with database configuration
- **WHEN** a user runs the API image with a valid `DATABASE_URL` pointing to PostgreSQL
- **THEN** the container starts the API server and can serve transaction and analytics endpoints

### Requirement: Container exposes API documentation
The containerized service SHALL expose FastAPI documentation endpoints.

#### Scenario: Swagger UI is available
- **WHEN** the containerized API is running and a client opens `http://localhost:8000/docs`
- **THEN** FastAPI Swagger UI is available

#### Scenario: OpenAPI schema is available
- **WHEN** the containerized API is running and a client opens `http://localhost:8000/openapi.json`
- **THEN** the OpenAPI schema is available

### Requirement: Runtime configuration
The system SHALL support database configuration through environment variables.

#### Scenario: Database URL is provided
- **WHEN** the service starts with `DATABASE_URL`
- **THEN** it uses that PostgreSQL database URL for application queries

#### Scenario: Compose environment is used
- **WHEN** the service starts through Docker Compose
- **THEN** the API receives a `DATABASE_URL` that points to the Compose PostgreSQL service
