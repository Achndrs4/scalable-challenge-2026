-- Fails if listens row count diverges from stg_listens (listens is a pure transform — no rows should be added or dropped).
SELECT 1
WHERE (SELECT COUNT(*) FROM {{ ref('listens') }})
   != (SELECT COUNT(*) FROM {{ ref('stg_listens') }})
