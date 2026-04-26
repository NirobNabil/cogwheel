## ADDED Requirements

### Requirement: Alembic migration setup
The system SHALL use Alembic to manage PostgreSQL schema changes.

#### Scenario: Alembic configuration exists
- **WHEN** a developer checks the repository
- **THEN** the repository includes Alembic configuration and an `alembic/versions` directory

#### Scenario: Migration command is available
- **WHEN** a developer runs `alembic upgrade head` with a valid PostgreSQL `DATABASE_URL`
- **THEN** Alembic applies all pending migrations

### Requirement: Initial transaction migration
The system SHALL include an initial migration that creates the transaction table.

#### Scenario: Initial migration is applied
- **WHEN** Alembic upgrades the database from an empty schema
- **THEN** the transaction table exists with columns for `id`, `property_name`, `category`, `price`, `quantity`, and `date`

#### Scenario: Price uses floating-point storage
- **WHEN** the transaction table is created
- **THEN** the `price` column uses a PostgreSQL-compatible floating-point type

### Requirement: Application does not create tables directly
The system SHALL rely on Alembic for schema creation instead of creating tables from application startup code.

#### Scenario: Application starts
- **WHEN** the FastAPI application starts
- **THEN** it does not call SQLAlchemy metadata table creation as a replacement for migrations
