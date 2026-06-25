import duckdb

from db import connect


def top_10_users(con: duckdb.DuckDBPyConnection) -> None:
    # Task 2a-i: Top 10 users by number of listens.
    print("\n── Top 10 users by listens ──")
    con.sql("""
        SELECT user_name, COUNT(*) AS listens
        FROM listens
        GROUP BY user_name
        ORDER BY listens DESC
        LIMIT 10
    """).show()


def users_on_march_1_2019(con: duckdb.DuckDBPyConnection) -> None:
    # Task 2a-ii: Number of users who listened on 2019-03-01.
    print("\n── Users who listened on 2019-03-01 ──")
    con.sql("""
        SELECT COUNT(DISTINCT user_name) AS user_count
        FROM listens
        WHERE listen_date = DATE '2019-03-01'
    """).show()


def first_song_per_user(con: duckdb.DuckDBPyConnection) -> None:
    # Task 2a-iii: First song ever listened to, per user.
    print("\n── First song per user ──")
    con.sql("""
        WITH ranked AS (
            SELECT
                user_name,
                track_name,
                artist_name,
                listened_at,
                ROW_NUMBER() OVER (
                    PARTITION BY user_name
                    ORDER BY listened_at ASC
                ) AS rn
            FROM listens
        )
        SELECT user_name, track_name, artist_name, listened_at
        FROM ranked
        WHERE rn = 1
        ORDER BY user_name
    """).show()


def top_3_days_per_user(con: duckdb.DuckDBPyConnection) -> None:
    # Task 2b: Top 3 days with most listens per user.
    print("\n── Top 3 listening days per user ──")
    con.sql("""
        WITH daily AS (
            SELECT
                user_name,
                listen_date AS date,
                COUNT(*)    AS number_of_listens
            FROM listens
            GROUP BY user_name, listen_date
        ),
        ranked AS (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY user_name
                    ORDER BY number_of_listens DESC
                ) AS rn
            FROM daily
        )
        SELECT user_name, number_of_listens, date
        FROM ranked
        WHERE rn <= 3
        ORDER BY user_name, number_of_listens DESC
    """).show()


def daily_active_users(con: duckdb.DuckDBPyConnection) -> None:
    print("\n── Daily active users (7-day rolling window) ──")
    con.sql("""
        WITH all_days AS (
            SELECT DISTINCT listen_date AS date FROM listens
        ),
        total_users AS (
            SELECT COUNT(DISTINCT user_name) AS total FROM listens
        ),
        active AS (
            SELECT
                d.date,
                COUNT(DISTINCT l.user_name) AS number_active_users
            FROM all_days d
            JOIN listens l
              ON l.listen_date BETWEEN d.date - INTERVAL 6 DAYS AND d.date
            GROUP BY d.date
        )
        SELECT
            a.date,
            a.number_active_users,
            ROUND(100.0 * a.number_active_users / t.total, 2) AS percentage_active_users
        FROM active a
        CROSS JOIN total_users t
        ORDER BY a.date
    """).show()


if __name__ == "__main__":
    con = connect()
    top_10_users(con)
    users_on_march_1_2019(con)
    first_song_per_user(con)
    top_3_days_per_user(con)
    daily_active_users(con)
    con.close()
