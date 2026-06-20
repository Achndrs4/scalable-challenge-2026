import json
import pytest
import duckdb
from conftest import VALID_RECORDS


def _insert(con: duckdb.DuckDBPyConnection, path: str) -> int:
    """Run the ingest SQL against an existing connection (bypasses db.connect())."""
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
                    user_name:      'VARCHAR',
                    recording_msid: 'VARCHAR',
                    listened_at:    'BIGINT',
                    track_metadata: 'STRUCT(
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
            WHERE user_name IS NOT NULL AND TRIM(user_name) != ''
              AND recording_msid IS NOT NULL AND TRIM(recording_msid) != ''
              AND listened_at > 0
        )
        SELECT s.* FROM source s
        WHERE NOT EXISTS (
            SELECT 1 FROM raw_listens r
            WHERE r.user_name        = s.user_name
              AND r.recording_msid   = s.recording_msid
              AND r.listened_at_unix = s.listened_at_unix
        )
    """)
    after = con.execute("SELECT COUNT(*) FROM raw_listens").fetchone()[0]
    return after - before


def test_first_run_inserts_all(db, valid_jsonl):
    inserted = _insert(db, valid_jsonl)
    assert inserted == len(VALID_RECORDS)


def test_second_run_inserts_nothing(db, valid_jsonl):
    _insert(db, valid_jsonl)
    inserted_again = _insert(db, valid_jsonl)
    assert inserted_again == 0


def test_total_count_unchanged_after_rerun(db, valid_jsonl):
    _insert(db, valid_jsonl)
    count_before = db.execute("SELECT COUNT(*) FROM raw_listens").fetchone()[0]
    _insert(db, valid_jsonl)
    count_after = db.execute("SELECT COUNT(*) FROM raw_listens").fetchone()[0]
    assert count_before == count_after


def test_invalid_timestamp_rejected(db, tmp_path):
    bad = [{"user_name": "u1", "recording_msid": "x", "listened_at": 0,
            "track_metadata": {"artist_name": "A", "track_name": "T",
                               "release_name": None,
                               "additional_info": {"artist_msid": None, "track_mbid": None, "spotify_id": None}}}]
    f = tmp_path / "bad.jsonl"
    f.write_text(json.dumps(bad[0]))
    inserted = _insert(db, str(f))
    assert inserted == 0
