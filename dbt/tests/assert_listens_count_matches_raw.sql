-- Fails if listens has fewer rows than raw_listens (rows silently dropped during transform).
SELECT 1
WHERE (SELECT COUNT(*) FROM {{ ref('listens') }})
    < (SELECT COUNT(*) FROM {{ source('raw', 'raw_listens') }})
