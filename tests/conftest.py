import json

import duckdb
import pytest

VALID_RECORDS = [
    {
        "user_name": "user_0001",
        "recording_msid": "aaaa-0001",
        "listened_at": 1551398400,
        "track_metadata": {
            "artist_name": "SAMPLE_ARTIST_1",
            "track_name": "SAMPLE_TRACK_1_1",
            "release_name": "SAMPLE_RELEASE_1",
            "additional_info": {"artist_msid": "m1", "track_mbid": None, "spotify_id": None},
        },
    },
    {
        "user_name": "user_0002",
        "recording_msid": "bbbb-0002",
        "listened_at": 1551484800,
        "track_metadata": {
            "artist_name": "SAMPLE_ARTIST_2",
            "track_name": "SAMPLE_TRACK_2_1",
            "release_name": None,
            "additional_info": {"artist_msid": None, "track_mbid": None, "spotify_id": None},
        },
    },
    {
        "user_name": "user_0001",
        "recording_msid": "cccc-0003",
        "listened_at": 1551571200,
        "track_metadata": {
            "artist_name": "SAMPLE_ARTIST_1",
            "track_name": "SAMPLE_TRACK_1_2",
            "release_name": None,
            "additional_info": {"artist_msid": None, "track_mbid": None, "spotify_id": None},
        },
    },
]


@pytest.fixture
def db():
    """Blank in-memory DuckDB with raw_listens schema, torn down after each test."""
    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE raw_listens (
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
    yield con
    con.close()


@pytest.fixture
def valid_jsonl(tmp_path):
    """Write VALID_RECORDS to a temp JSONL file and return its path."""
    f = tmp_path / "test.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in VALID_RECORDS))
    return str(f)


@pytest.fixture
def mixed_jsonl(tmp_path):
    """JSONL file mixing valid records with malformed lines."""
    lines = [
        json.dumps(VALID_RECORDS[0]),
        "not json at all",
        '{"user_name":}',
        "[1, 2, 3]",
        "",
        json.dumps(VALID_RECORDS[1]),
    ]
    f = tmp_path / "mixed.jsonl"
    f.write_text("\n".join(lines))
    return str(f)
