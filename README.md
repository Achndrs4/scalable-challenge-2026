# Scalable Capital Challenge 2026

## Installation
Instructions on installation can be found in SETUP.MD; This section involves an explination of design decisions and some differences between this simple test program and a productionalized setup.

## File Validation
The first step of this pipeline is ingesting our jsonl file with records. We do this by splititng the read into different process pools and validating multiple lines simultanously, until we have a filtered outfile in terms of format (though not in terms of the actual data its meant to represent). This should be done here as the functionality of duckdb's schema inference can be unexpected with broken jsonls.

## Ingestion into DB
Now, we take this cleaned file and run some checks on each row of the cleaned file. THis includes trimming whitespace, normalizing empty strings, filtering duplicates in the ingestion file as well as filtering duplicates which already exist in the database. This makes our pipeline idempotent.

## Business Logic With DBT
While the previous step gave us a valid raw database with all of the "transactions" we need, we cannot and should not be expected to query this table with complex business queries and it will result in backpressure for the ingestion pipeline. Therefore, we create a materialized table, which currently is ordered by listen date and user name to anticipate business use cases and optimize by having sequential memory blocks in the DB.

## Data Tests
To ensure that changes in our model don't break the expected downstream, we have defined some dbt tests that include null checks, as well as singular sql tests that check, for example, that we don't have duplicates and also that dbt itself doesn't drop anything between listens and raw_listens, for example.