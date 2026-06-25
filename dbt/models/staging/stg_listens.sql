{{ config(
    materialized='incremental',
    unique_key=['user_name', 'recording_msid', 'listened_at_unix'],
    incremental_strategy='delete+insert',
    on_schema_change='sync_all_columns'
) }}

WITH filtered AS (
    SELECT
        user_name,
        recording_msid,
        listened_at_unix,
        TRIM(artist_name)  AS artist_name,
        TRIM(track_name)   AS track_name,
        release_name,
        artist_msid,
        track_mbid,
        spotify_id,
        batch_timestamp,
        batch_id
    FROM {{ ref('raw_listens') }}
    WHERE user_name IS NOT NULL AND TRIM(user_name) != ''
      AND recording_msid IS NOT NULL AND TRIM(recording_msid) != ''
      AND listened_at_unix > 0
    {% if is_incremental() %}
      AND batch_timestamp > (SELECT MAX(batch_timestamp) FROM {{ this }})
    {% endif %}
),

deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY user_name, recording_msid, listened_at_unix
            ORDER BY batch_timestamp DESC
        ) AS rn
    FROM filtered
)

SELECT * EXCLUDE (rn)
FROM deduped
WHERE rn = 1
