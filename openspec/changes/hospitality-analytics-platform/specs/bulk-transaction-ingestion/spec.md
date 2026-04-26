## ADDED Requirements

### Requirement: Bulk JSON transaction ingestion
The system SHALL expose `POST /transactions/bulk` to create multiple transactions from a JSON array while allowing partial success.

#### Scenario: Successful JSON bulk ingestion
- **WHEN** a client submits a JSON array of valid transaction payloads to `POST /transactions/bulk`
- **THEN** the API stores every transaction in the array and returns a summary with inserted count, failed count, and created records or IDs

#### Scenario: Mixed-validity JSON bulk ingestion
- **WHEN** a client submits a JSON array containing valid and invalid transaction payloads
- **THEN** the API stores the valid transactions, skips invalid transactions, and returns item-level errors for invalid entries

#### Scenario: JSON bulk has no valid entries
- **WHEN** a client submits a JSON array with no valid transaction payloads
- **THEN** the API stores no transactions and returns a summary showing zero inserted records and errors for invalid entries

### Requirement: CSV upload endpoint
The system SHALL expose `POST /transactions/upload-csv` to upload transaction data using a multipart `.csv` file field compatible with Swagger UI.

#### Scenario: Swagger-compatible CSV upload
- **WHEN** a client opens the generated Swagger UI for `POST /transactions/upload-csv`
- **THEN** the endpoint accepts a file upload field named `file`

#### Scenario: CSV file is submitted
- **WHEN** a client submits a `.csv` file to `POST /transactions/upload-csv`
- **THEN** the API parses the uploaded file as CSV transaction data

### Requirement: CSV schema validation
The system SHALL require CSV files to include `property_name`, `category`, `price`, `quantity`, and `date` columns.

#### Scenario: CSV has required headers
- **WHEN** an uploaded CSV file includes all required columns
- **THEN** the API validates rows using those columns

#### Scenario: CSV is missing required headers
- **WHEN** an uploaded CSV file is missing one or more required columns
- **THEN** the API rejects the file and stores no transactions from that file

### Requirement: CSV partial-success ingestion
The system SHALL store valid CSV rows and report invalid CSV rows.

#### Scenario: CSV contains all valid rows
- **WHEN** an uploaded CSV file contains only valid transaction rows
- **THEN** the API stores every row and returns a summary with inserted count equal to the number of rows

#### Scenario: CSV contains valid and invalid rows
- **WHEN** an uploaded CSV file contains a mix of valid and invalid transaction rows
- **THEN** the API stores the valid rows, skips the invalid rows, and returns inserted count, failed count, and row-level errors

#### Scenario: CSV contains no valid rows
- **WHEN** an uploaded CSV file contains rows but none are valid transactions
- **THEN** the API stores no transactions and returns a summary showing zero inserted rows and row-level errors

### Requirement: CSV values use transaction validation rules
The system SHALL apply the same simple transaction validation rules to CSV rows that it applies to JSON transaction creation.

#### Scenario: CSV row has invalid values
- **WHEN** a CSV row has an invalid `price`, invalid `quantity`, invalid `date`, or missing required value
- **THEN** that row is reported as invalid and is not stored

### Requirement: Bulk and CSV date format
The system SHALL require `DD-MM-YYYY` dates in JSON bulk records and CSV rows.

#### Scenario: JSON bulk date format
- **WHEN** a JSON bulk item includes `date` equal to `01-04-2026`
- **THEN** the item is treated as a valid calendar-date value

#### Scenario: CSV date format
- **WHEN** a CSV row includes `date` equal to `01-04-2026`
- **THEN** the row is treated as a valid calendar-date value

#### Scenario: Invalid bulk or CSV date format
- **WHEN** a JSON bulk item or CSV row includes a date that is not in `DD-MM-YYYY` format
- **THEN** that item or row is reported as invalid and is not stored
