## ADDED Requirements

### Requirement: Total sales analytics
The system SHALL expose `GET /analytics/total-sales` to return total revenue across all persisted transactions.

#### Scenario: Total sales with transactions
- **WHEN** persisted transactions exist with `price` and `quantity`
- **THEN** `GET /analytics/total-sales` returns the sum of `price * quantity` across all transactions

#### Scenario: Total sales with no transactions
- **WHEN** no transactions are persisted
- **THEN** `GET /analytics/total-sales` returns total sales as zero

### Requirement: Top properties analytics
The system SHALL expose `GET /analytics/top-properties` to return the top three properties by revenue.

#### Scenario: Top properties are ranked by revenue
- **WHEN** transactions exist for more than one `property_name`
- **THEN** `GET /analytics/top-properties` groups transactions by `property_name` and orders properties by total revenue descending

#### Scenario: Top properties returns at most three properties
- **WHEN** transactions exist for more than three properties
- **THEN** `GET /analytics/top-properties` returns only the three highest-revenue properties

#### Scenario: Top properties with fewer than three properties
- **WHEN** transactions exist for fewer than three properties
- **THEN** `GET /analytics/top-properties` returns all properties with revenue

#### Scenario: Top properties with no transactions
- **WHEN** no transactions are persisted
- **THEN** `GET /analytics/top-properties` returns an empty list

### Requirement: Analytics revenue calculation
The system SHALL calculate analytics revenue from persisted transaction floating-point `price` and integer `quantity`.

#### Scenario: Revenue uses quantity
- **WHEN** a transaction has `price` of `100.5` and `quantity` of `3`
- **THEN** analytics include `301.5` revenue contribution for that transaction

#### Scenario: Revenue aggregates multiple transactions per property
- **WHEN** multiple transactions share the same `property_name`
- **THEN** top properties analytics sums revenue across those transactions for that property

### Requirement: Analytics deterministic ties
The system SHALL return deterministic ordering when multiple properties have the same revenue.

#### Scenario: Equal revenue tie
- **WHEN** two properties have the same total revenue
- **THEN** `GET /analytics/top-properties` orders those tied properties by `property_name` ascending

### Requirement: Analytics response structure
The system SHALL return structured JSON responses for analytics endpoints.

#### Scenario: Total sales response structure
- **WHEN** a client calls `GET /analytics/total-sales`
- **THEN** the API response includes a `total_sales` value

#### Scenario: Top properties response structure
- **WHEN** a client calls `GET /analytics/top-properties`
- **THEN** the API response includes a list of entries containing `property_name` and `revenue`

### Requirement: Analytics are global
The system SHALL keep analytics endpoints global for this assignment.

#### Scenario: Analytics request with no filters
- **WHEN** a client calls an analytics endpoint
- **THEN** the API aggregates across all stored transactions without requiring category or date filters
