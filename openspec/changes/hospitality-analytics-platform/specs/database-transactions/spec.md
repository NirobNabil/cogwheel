## ADDED Requirements

### Requirement: Database sessions
The system SHALL perform database interactions through SQLAlchemy sessions provided by the application database dependency.

#### Scenario: Endpoint uses database session
- **WHEN** an endpoint needs to read or write persisted transaction data
- **THEN** it uses the configured SQLAlchemy session dependency instead of opening ad hoc database connections

### Requirement: ACID write transactions
The system SHALL wrap database write operations in explicit ACID transactions.

#### Scenario: Single create commit
- **WHEN** `POST /transactions` successfully persists a transaction
- **THEN** the database transaction is committed before the response is returned

#### Scenario: Bulk create commit
- **WHEN** `POST /transactions/bulk` has one or more valid records
- **THEN** all valid records for that request are persisted within a single committed database transaction

#### Scenario: CSV upload commit
- **WHEN** `POST /transactions/upload-csv` has one or more valid rows
- **THEN** all valid rows for that request are persisted within a single committed database transaction

### Requirement: Rollback on database failure
The system SHALL rollback the active database transaction when a database write operation fails.

#### Scenario: Single create rollback
- **WHEN** `POST /transactions` encounters a database exception while writing
- **THEN** the active transaction is rolled back and no partial write remains

#### Scenario: Bulk create rollback
- **WHEN** `POST /transactions/bulk` encounters a database exception while writing valid records
- **THEN** the active transaction is rolled back and none of that request's valid records remain partially persisted

#### Scenario: CSV upload rollback
- **WHEN** `POST /transactions/upload-csv` encounters a database exception while writing valid rows
- **THEN** the active transaction is rolled back and none of that request's valid rows remain partially persisted

### Requirement: Read operations avoid writes
The system SHALL keep read-only database interactions free of commit side effects.

#### Scenario: Transaction list read
- **WHEN** `GET /transactions` reads persisted transactions
- **THEN** it does not commit or mutate transaction data

#### Scenario: Analytics read
- **WHEN** an analytics endpoint reads persisted transactions
- **THEN** it does not commit or mutate transaction data
