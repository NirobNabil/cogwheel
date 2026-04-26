## ADDED Requirements

### Requirement: Transaction data model
The system SHALL persist hospitality transactions with an auto-generated `id`, `property_name`, `category`, `price`, `quantity`, and `date`.

#### Scenario: Persisted transaction includes required fields
- **WHEN** a valid transaction is stored
- **THEN** the persisted record includes a generated integer `id`, non-empty `property_name`, non-empty `category`, floating-point `price`, integer `quantity`, and calendar `date`

#### Scenario: Revenue can be derived from a transaction
- **WHEN** a persisted transaction has `price` and `quantity`
- **THEN** the system can calculate that transaction revenue as `price * quantity`

### Requirement: Transaction input validation
The system SHALL validate transaction input before persistence using simple assignment-focused validation rules.

#### Scenario: Valid transaction payload
- **WHEN** a transaction payload includes non-empty `property_name`, non-empty `category`, `price` greater than zero, `quantity` greater than zero, and `date` in `DD-MM-YYYY` format
- **THEN** the payload is accepted for persistence

#### Scenario: Missing required field
- **WHEN** a transaction payload omits any required field
- **THEN** the API rejects the payload with a validation error and stores no transaction from that payload

#### Scenario: Invalid numeric values
- **WHEN** a transaction payload includes `price` less than or equal to zero or `quantity` less than or equal to zero
- **THEN** the API rejects the payload with a validation error and stores no transaction from that payload

#### Scenario: Invalid date value
- **WHEN** a transaction payload includes a `date` that is not a valid `DD-MM-YYYY` calendar date
- **THEN** the API rejects the payload with a validation error and stores no transaction from that payload

### Requirement: Create a single transaction
The system SHALL expose `POST /transactions` to create one transaction.

#### Scenario: Successful single transaction creation
- **WHEN** a client submits a valid transaction payload to `POST /transactions`
- **THEN** the API stores the transaction and returns the created transaction including its generated `id`

#### Scenario: Invalid single transaction creation
- **WHEN** a client submits an invalid transaction payload to `POST /transactions`
- **THEN** the API returns a validation error and does not create a transaction

### Requirement: Transaction date response format
The system SHALL return transaction dates in `DD-MM-YYYY` format.

#### Scenario: Created transaction date format
- **WHEN** a transaction is created with `date` equal to `01-04-2026`
- **THEN** the API response includes `date` equal to `01-04-2026`

#### Scenario: Listed transaction date format
- **WHEN** a client retrieves transactions through `GET /transactions`
- **THEN** every returned transaction uses `DD-MM-YYYY` for `date`

### Requirement: List transactions
The system SHALL expose `GET /transactions` to retrieve stored transactions.

#### Scenario: Retrieve all transactions without filters
- **WHEN** a client calls `GET /transactions` without query parameters
- **THEN** the API returns all persisted transactions

#### Scenario: Retrieve transactions from an empty database
- **WHEN** no transactions have been stored
- **THEN** `GET /transactions` returns an empty list

### Requirement: Filter transactions by category
The system SHALL support filtering `GET /transactions` by `category`.

#### Scenario: Category filter returns matching transactions
- **WHEN** a client calls `GET /transactions?category=food`
- **THEN** the API returns only transactions whose `category` matches `food`

#### Scenario: Category filter has no matches
- **WHEN** a client filters by a category that has no stored transactions
- **THEN** the API returns an empty list

### Requirement: Filter transactions by date range
The system SHALL support filtering `GET /transactions` by optional `start_date` and `end_date` query parameters in `DD-MM-YYYY` format.

#### Scenario: Start date filter
- **WHEN** a client calls `GET /transactions?start_date=01-04-2026`
- **THEN** the API returns only transactions with `date` on or after `01-04-2026`

#### Scenario: End date filter
- **WHEN** a client calls `GET /transactions?end_date=30-04-2026`
- **THEN** the API returns only transactions with `date` on or before `30-04-2026`

#### Scenario: Inclusive date range filter
- **WHEN** a client calls `GET /transactions?start_date=01-04-2026&end_date=30-04-2026`
- **THEN** the API returns only transactions with `date` between `01-04-2026` and `30-04-2026`, inclusive

#### Scenario: Invalid date filter
- **WHEN** a client provides an invalid `start_date` or `end_date`
- **THEN** the API returns a validation error and does not execute a filtered query

#### Scenario: Start date after end date
- **WHEN** a client provides `start_date` later than `end_date`
- **THEN** the API returns a validation error

### Requirement: Combined transaction filters
The system SHALL allow `category`, `start_date`, and `end_date` filters to be combined.

#### Scenario: Combined filters return intersection
- **WHEN** a client calls `GET /transactions` with `category`, `start_date`, and `end_date`
- **THEN** the API returns only transactions matching the category and falling within the inclusive date range

### Requirement: Transaction response ordering
The system SHALL return transactions in deterministic order.

#### Scenario: List order is deterministic
- **WHEN** a client retrieves transactions through `GET /transactions`
- **THEN** the API returns transactions ordered by `date` ascending and then `id` ascending
