-- Fails if any (user_name, recording_msid, listened_at) combination appears more than once.
SELECT user_name, recording_msid, listened_at, COUNT(*) AS cnt
FROM {{ ref('listens') }}
GROUP BY user_name, recording_msid, listened_at
HAVING COUNT(*) > 1
