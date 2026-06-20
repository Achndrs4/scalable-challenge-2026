"""
Generates a large JSONL dataset for pipeline scale and robustness testing.

Produces four categories of records, shuffled together:
  - Valid records    : well-formed listens matching the real schema
  - Duplicates       : exact copies of valid records (pipeline must skip these)
  - Invalid records  : valid JSON but missing required fields or bad timestamps (pipeline must reject)
  - Malformed lines  : unparseable JSON (pipeline must skip via ignore_errors)
"""

import json
import uuid
import random
from pathlib import Path

NUM_VALID      = 100_000
NUM_DUPLICATES = 2_000
NUM_INVALID    = 500
NUM_MALFORMED  = 200
SEED           = 42
OUTPUT         = Path(__file__).parent / "large_sample.jsonl"

NUM_ARTISTS = 10
NUM_TRACKS  = 5
NUM_USERS   = 500

START_TS = 1546300800  # 2019-01-01
END_TS   = 1577836799  # 2019-12-31

ARTISTS = [
    (f"SAMPLE_ARTIST_{i}", [f"SAMPLE_TRACK_{i}_{j}" for j in range(1, NUM_TRACKS + 1)])
    for i in range(1, NUM_ARTISTS + 1)
]
USERS = [f"SAMPLE_USER_{i:04d}" for i in range(1, NUM_USERS + 1)]


def _uuid(rng: random.Random) -> str:
    return str(uuid.UUID(int=rng.getrandbits(128)))


def make_valid(rng: random.Random) -> dict:
    artist_name, tracks = rng.choice(ARTISTS)
    return {
        "track_metadata": {
            "additional_info": {
                "artist_msid":    _uuid(rng),
                "recording_msid": _uuid(rng),
                "spotify_id":     f"spotify:track:{_uuid(rng)}" if rng.random() > 0.3 else None,
                "track_mbid":     _uuid(rng) if rng.random() > 0.5 else None,
                "artist_mbids":   [],
                "tags":           [],
            },
            "artist_name":  artist_name,
            "track_name":   rng.choice(tracks),
            "release_name": f"SAMPLE_RELEASE_{artist_name}",
        },
        "listened_at":    rng.randint(START_TS, END_TS),
        "recording_msid": _uuid(rng),
        "user_name":      rng.choice(USERS),
    }


def make_invalids(rng: random.Random) -> list:
    per_type = NUM_INVALID // 5
    invalids = []
    for mutation in [
        lambda r: r.update({"user_name": None}),
        lambda r: r.update({"recording_msid": None}),
        lambda r: r.update({"listened_at": 0}),
        lambda r: r.update({"listened_at": -1}),
        lambda r: r.pop("track_metadata"),
    ]:
        for _ in range(per_type):
            r = make_valid(rng)
            mutation(r)
            invalids.append(r)
    return invalids


MALFORMED_LINES = [
    "not json at all",
    '{"user_name": "missing_closing_brace"',
    '{"user_name":}',
    "",
    "   ",
    '[1, 2, 3]',
    '{"user_name": "SAMPLE_USER_0001", "listened_at": 123, UNQUOTED_KEY: true}',
]


def main() -> None:
    rng = random.Random(SEED)

    valid      = [make_valid(rng) for _ in range(NUM_VALID)]
    duplicates = rng.choices(valid, k=NUM_DUPLICATES)
    invalids   = make_invalids(rng)
    malformed  = [rng.choice(MALFORMED_LINES) for _ in range(NUM_MALFORMED)]

    # mix JSON records and raw malformed strings together
    json_lines = [json.dumps(r) for r in valid + duplicates + invalids]
    all_lines  = json_lines + malformed
    rng.shuffle(all_lines)

    with OUTPUT.open("w") as f:
        for line in all_lines:
            f.write(line + "\n")

    print(f"Written {len(all_lines):,} lines to {OUTPUT}")
    print(f"  {NUM_VALID:,} valid | {NUM_DUPLICATES:,} duplicates | {NUM_INVALID:,} invalid | {NUM_MALFORMED:,} malformed")


if __name__ == "__main__":
    main()
