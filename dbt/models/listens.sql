SELECT
    user_name,
    recording_msid,
    to_timestamp(listened_at_unix)               AS listened_at,
    CAST(to_timestamp(listened_at_unix) AS DATE) AS listen_date,
    COALESCE(artist_name, 'Unknown')             AS artist_name,
    COALESCE(track_name,  'Unknown')             AS track_name,
    release_name,
    spotify_id
FROM {{ ref('stg_listens') }}