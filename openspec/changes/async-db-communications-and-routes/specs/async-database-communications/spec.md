## ADDED Requirements

### Requirement: Runtime database access uses async SQLAlchemy sessions
The system SHALL use SQLAlchemy async engine and `AsyncSession` based session management for application runtime database communication.

#### Scenario: Creating a request database session
- **WHEN** a request needs database access
- **THEN** the database dependency yields an `AsyncSession` from an async session factory

#### Scenario: Completing request database access
- **WHEN** request handling finishes
- **THEN** the async database dependency closes the session without blocking the event loop

### Requirement: Repository database operations are awaitable
The system SHALL implement repository functions that perform database I/O as async functions and SHALL await SQLAlchemy async session methods.

#### Scenario: Writing transactions
- **WHEN** a repository creates one or more transaction records
- **THEN** it awaits add-related flush/commit/refresh behavior as required by SQLAlchemy async session usage

#### Scenario: Reading transactions and analytics
- **WHEN** a repository lists transactions or calculates analytics
- **THEN** it awaits async query execution and returns materialized response data

### Requirement: Services use async database communication
The system SHALL expose async service functions for all database-backed business operations and SHALL await repository calls.

#### Scenario: Creating data through a service
- **WHEN** a controller calls a transaction creation or ingestion service
- **THEN** the service awaits the repository write operation before constructing the API response

#### Scenario: Reading data through a service
- **WHEN** a controller calls transaction listing or analytics services
- **THEN** the service awaits repository read operations before constructing the API response

### Requirement: Async write operations preserve transaction semantics
The system SHALL preserve existing write transaction behavior by committing once on successful writes and rolling back on database write failures.

#### Scenario: Successful write
- **WHEN** a single or bulk transaction write succeeds
- **THEN** the async session commits the write and refreshes returned records before the response is produced

#### Scenario: Failed write
- **WHEN** a database write or commit fails
- **THEN** the async session rolls back the attempted write and the API returns the existing database-write failure response

### Requirement: Async read operations remain read-only
The system SHALL keep read-only transaction and analytics operations from committing or rolling back database sessions during normal successful reads.

#### Scenario: Successful read
- **WHEN** a client lists transactions or requests analytics
- **THEN** the async session executes the required read query without commit or rollback side effects

### Requirement: Verification uses async database fixtures
The system MUST update automated tests and fixtures so they exercise async database sessions, async dependency overrides, and async route handlers.

#### Scenario: Running automated tests
- **WHEN** the test suite runs
- **THEN** database-backed API tests use async-compatible sessions and still verify validation, persistence, filtering, analytics, commits, rollbacks, and read-only behavior
