## ADDED Requirements

### Requirement: Bruno collection structure
The system SHALL include a Bruno collection for manual API verification.

#### Scenario: Bruno collection exists
- **WHEN** a developer opens the repository
- **THEN** the repository includes `bruno/hospitality-analytics-platform/bruno.json`

#### Scenario: Bruno environments exist
- **WHEN** a developer opens the Bruno collection
- **THEN** it includes `environments/Local.bru` and `environments/Local.json`

#### Scenario: Bruno base URL variable exists
- **WHEN** a Bruno request uses the API base URL
- **THEN** it references a `baseUrl` environment variable with local default `http://localhost:8000`

### Requirement: Bruno transaction request variations
The Bruno collection SHALL include request variations for transaction creation and listing.

#### Scenario: Create transaction requests
- **WHEN** a developer opens the Transactions request group
- **THEN** it includes requests for valid create, missing required field, invalid price, and invalid `DD-MM-YYYY` date

#### Scenario: List transaction requests
- **WHEN** a developer opens the Transactions request group
- **THEN** it includes requests for list all, filter by category, filter by start date, filter by end date, filter by date range, and combined category/date filters

### Requirement: Bruno bulk ingestion variations
The Bruno collection SHALL include request variations for JSON bulk ingestion.

#### Scenario: Bulk JSON requests
- **WHEN** a developer opens the Bulk Upload request group
- **THEN** it includes requests for all-valid bulk create, mixed valid/invalid bulk create, and all-invalid bulk create

### Requirement: Bruno CSV upload variations
The Bruno collection SHALL include request variations for CSV upload ingestion.

#### Scenario: CSV upload requests
- **WHEN** a developer opens the CSV Upload request group
- **THEN** it includes requests for valid CSV upload, mixed valid/invalid CSV upload, and missing-header CSV upload

### Requirement: Bruno analytics variations
The Bruno collection SHALL include request variations for analytics endpoints.

#### Scenario: Analytics requests
- **WHEN** a developer opens the Analytics request group
- **THEN** it includes requests for total sales and top properties

### Requirement: Bruno assertions and variables
The Bruno requests SHALL include lightweight post-response checks or variable capture where useful.

#### Scenario: Create request captures id
- **WHEN** the valid create transaction request succeeds
- **THEN** the Bruno script stores the created transaction id in an environment variable

#### Scenario: Response checks exist
- **WHEN** a Bruno request expects success or validation failure
- **THEN** the request includes a simple status-code check in a post-response script where practical

### Requirement: Unit test verification
The system SHALL include unit tests for implementation verification.

#### Scenario: AI verifies implementation
- **WHEN** implementation work is completed or modified
- **THEN** the AI runs the unit test command and reports the result

#### Scenario: Unit test coverage
- **WHEN** the unit test suite is run
- **THEN** it covers transaction validation, date parsing, filtered listing, JSON bulk partial success, CSV partial success, analytics calculations, and database commit/rollback behavior
