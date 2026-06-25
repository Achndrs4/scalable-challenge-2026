# Scalable Capital Challenge 2026

## Installation
Instructions on installation can be found in [Readme.md](Readme.md). This section covers design decisions and differences between this pipeline and a fully productionised setup.

## File Validation
The first step of this pipeline is ingesting our jsonl file with records. We do this by splitting the read into different process pools and validating multiple lines simultanously, until we have a filtered outfile in terms of format (though not in terms of the actual data its meant to represent). This should be done here, and not by DBT, because the "cleanup" here does not involve business logic - simply validation that the file can be parsed, and if not, at least partially parsed. We also add a batch timestamp so that if newer data comes in we overwrite.

In an actual AWS setup, we probably would have an S3 Bucket wired with something like SQS, with notifications to a new service on write that can either process small files (so, something like Lambda alone would be enough) - or for larger files (something like Spark) that can coorfinate I/O operations across several machines. The validated files should also live on S3, expecially in services that require regulatory oversight. This would then kick off the next part of the pipeline, ingestion.

## DB Ingestion
While the previous step gave us a valid raw file with all of the "transactions" we need, we now need to apply some filtering and splitting for analysis. Our staging table filters for meaningless requests (like without a user_name) and de-duplicates our rows. The unique key here, user_name, recording_msid, and listened_at are using an upsert strategy - so if a file comes in with bad values somehow (for example, an upstream service which drops off the S3 file messed up all artist titles with an umlaut), we can re-run it, and fix it.

## Business Logic / Semantic Layer
Now, with this table, we can create a table that's dedicated for business queries. Having it on a seperate table guarentees the I/O does not overlap with either of the above two flows. The table was chosen to interact neatly with the saved queries, but in other situations with differnet keys, a different solution can always be proposed that matches the shape of the data request.