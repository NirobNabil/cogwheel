# Assignment: Hospitality Analytics Platform

Imagine you’ve joined a company that operates across the hospitality industry (hotels, resorts, and restaurants). Each month, they receive operational and sales data from multiple sources, but currently there is no centralized system to store and analyze this data.

Your task is to build a lightweight backend service that allows the company to:

- Store incoming transaction data  
- Retrieve filtered data  
- Generate simple business insights  
- Upload bulk data via CSV  

---

## Your Goal

Build a FastAPI-based service that:

1. Accepts transaction data via API  
2. Supports CSV file upload for bulk data ingestion  
3. Stores data in a database  
4. Provides basic analytics endpoints  
5. Runs inside a Docker container  

---

## Requirements

### 1. Tech Stack

- Python  
- FastAPI  
- SQLAlchemy  
- SQLite (or PostgreSQL if preferred)  
- Docker  

---

### 2. Data Model

Each transaction should include:

- id (auto-generated)  
- property_name (e.g., hotel or restaurant name)  
- category (e.g., room booking, food, service)  
- price  
- quantity  
- date  

---

### 3. What the Business Needs (API Endpoints)

#### A. Add New Data

- `POST /transactions`

#### B. Bulk Upload (JSON)

- `POST /transactions/bulk`

#### C. CSV Upload

The business team often receives data in CSV format and wants to upload it directly from the API interface.

- `POST /transactions/upload-csv`  
- Accept a `.csv` file upload via API (Swagger UI should support this)  
- Parse and store all valid records  

#### D. View Transactions

- `GET /transactions`

Optional filters:

- category  
- start_date, end_date  

#### E. Business Insights (Analytics)

- `GET /analytics/total-sales`  
- `GET /analytics/top-properties` (top 3 by revenue)  

---

## Deployment Requirement (Docker)

- Provide a Dockerfile  
- The app should run using:

```bash
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app