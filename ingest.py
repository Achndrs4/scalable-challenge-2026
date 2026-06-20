from prefect import task
from db import connect, DATA_PATH


@task(name="Setup Schema", retries=2, retry_delay_seconds=10)
def setup() -> None:
    con = connect()
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_listens (
            user_name        VARCHAR NOT NULL,
            recording_msid   VARCHAR NOT NULL,
            listened_at_unix BIGINT  NOT NULL,
            artist_name      VARCHAR,
            track_name       VARCHAR,
            release_name     VARCHAR,
            artist_msid      VARCHAR,
            track_mbid       VARCHAR,
            spotify_id       VARCHAR
        )
    """)
    con.close()


@task(name="Ingest Raw Data", retries=3, retry_delay_seconds=30)
def ingest(path: str = DATA_PATH) -> int:
    """
    Load pre-validated JSONL into raw_listens. Idempotent:
    - skips rows already present (matched on user + recording + timestamp)
    - rejects rows with null or empty required keys, or invalid timestamps
    - deduplicates within the source file itself
    - trims whitespace from all string fields
    - normalises empty optional strings to NULL
    Returns the count of newly inserted rows.
    """
    con = connect()
    before = con.execute("SELECT COUNT(*) FROM raw_listens").fetchone()[0]

    con.execute(f"""
        INSERT INTO raw_listens (
            user_name, recording_msid, listened_at_unix,
            artist_name, track_name, release_name,
            artist_msid, track_mbid, spotify_id
        )
        WITH source AS (
            SELECT DISTINCT
                TRIM(user_name)                                       AS user_name,
                TRIM(recording_msid)                                  AS recording_msid,
                listened_at                                           AS listened_at_unix,
                NULLIF(TRIM(track_metadata.artist_name),  '')         AS artist_name,
                NULLIF(TRIM(track_metadata.track_name),   '')         AS track_name,
                NULLIF(TRIM(track_metadata.release_name), '')         AS release_name,
                track_metadata.additional_info.artist_msid            AS artist_msid,
                track_metadata.additional_info.track_mbid             AS track_mbid,
                track_metadata.additional_info.spotify_id             AS spotify_id
            FROM read_json('{path}',
                columns={{
                    user_name:        'VARCHAR',
                    recording_msid:   'VARCHAR',
                    listened_at:      'BIGINT',
                    track_metadata:   'STRUCT(
                        artist_name  VARCHAR,
                        track_name   VARCHAR,
                        release_name VARCHAR,
                        additional_info STRUCT(
                            artist_msid VARCHAR,
                            track_mbid  VARCHAR,
                            spotify_id  VARCHAR
                        )
                    )'
                }}
            )
            WHERE user_name IS NOT NULL
              AND TRIM(user_name) != ''
              AND recording_msid IS NOT NULL
              AND TRIM(recording_msid) != ''
              AND listened_at > 0
        )
        SELECT s.*
        FROM source s
        WHERE NOT EXISTS (
            SELECT 1 FROM raw_listens r
            WHERE r.user_name        = s.user_name
              AND r.recording_msid   = s.recording_msid
              AND r.listened_at_unix = s.listened_at_unix
        )
    """)

    after = con.execute("SELECT COUNT(*) FROM raw_listens").fetchone()[0]
    con.close()
    return after - before
