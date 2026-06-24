-- Fails if listens has fewer rows than stg_listens (rows silently dropped during semantic transform).
SELECT 1
WHERE (SELECT COUNT(*) FROM {{ ref('listens') }})
    < (SELECT COUNT(*) FROM {{ ref('stg_listens') }})
