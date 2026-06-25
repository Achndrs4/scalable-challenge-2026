{{ config(materialized='incremental', on_schema_change='sync_all_columns') }}

SELECT
    user_name,
    recording_msid,
    listened_at                                 AS listened_at_unix,
    track_metadata.artist_name                  AS artist_name,
    track_metadata.track_name                   AS track_name,
    track_metadata.release_name                 AS release_name,
    track_metadata.additional_info.artist_msid  AS artist_msid,
    track_metadata.additional_info.track_mbid   AS track_mbid,
    track_metadata.additional_info.spotify_id   AS spotify_id,
    epoch_us(now())::BIGINT                       AS batch_timestamp,
    '{{ invocation_id }}'                         AS batch_id
FROM read_json(
    '{{ var("data_path") }}',
    columns = {
        'user_name':      'VARCHAR',
        'recording_msid': 'VARCHAR',
        'listened_at':    'BIGINT',
        'track_metadata': 'STRUCT(
            artist_name  VARCHAR,
            track_name   VARCHAR,
            release_name VARCHAR,
            additional_info STRUCT(
                artist_msid VARCHAR,
                track_mbid  VARCHAR,
                spotify_id  VARCHAR
            )
        )'
    }
)
