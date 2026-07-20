import os
from datetime import datetime

from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URLが設定されていません。"
    )


# Supabase PostgreSQLへの接続を使い回す。
# Gunicornの各ワーカーごとに、この接続プールが作成される。
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=5,
    timeout=10,
    max_idle=120,
    max_lifetime=600,
    check=ConnectionPool.check_connection,
    kwargs={
        "row_factory": dict_row,
    },
    open=True,
)

print("========================================")
print("ConnectionPool initialized successfully")
print("========================================")

def get_connection():
    """
    Supabase PostgreSQLの接続プールから
    接続を取得する。

    with文を抜けると接続は切断されず、
    接続プールへ返却される。
    """

    try:
        stats = pool.get_stats()

        print("========== ConnectionPool ==========")
        print(f"connections_num : {stats.get('connections_num')}")
        print(f"pool_available  : {stats.get('pool_available')}")
        print(f"requests_waiting: {stats.get('requests_waiting')}")
        print("====================================")

    except Exception as error:
        print("ConnectionPool get_stats failed:", error)

    return pool.connection()


def create_table():
    """
    ランキング用テーブルと採点済みプロフィール用テーブル、
    および検索・順位計算用インデックスを作成する。

    すでに存在する場合は何もしない。
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ranking_entries (
                    uid BIGINT PRIMARY KEY,
                    nickname TEXT NOT NULL,
                    icon_url TEXT,
                    profile_value INTEGER NOT NULL DEFAULT 0,
                    total_score INTEGER NOT NULL DEFAULT 0,
                    rank_name TEXT NOT NULL,
                    achievements INTEGER NOT NULL DEFAULT 0,
                    theater_act INTEGER NOT NULL DEFAULT 0,
                    theater_stars INTEGER NOT NULL DEFAULT 0,
                    friendship_count INTEGER NOT NULL DEFAULT 0,
                    abyss_stars INTEGER NOT NULL DEFAULT 0,
                    stygian_difficulty INTEGER NOT NULL DEFAULT 0,
                    stygian_clear_time INTEGER NOT NULL DEFAULT 0,
                    server TEXT NOT NULL DEFAULT 'unknown',
                    updated_at TIMESTAMPTZ NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS scored_profiles (
                    uid BIGINT PRIMARY KEY,
                    profile_value INTEGER NOT NULL DEFAULT 0,
                    total_score INTEGER NOT NULL DEFAULT 0,
                    rank_name TEXT NOT NULL,
                    server TEXT NOT NULL DEFAULT 'unknown',
                    updated_at TIMESTAMPTZ NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                ranking_profile_value_idx
                ON ranking_entries (
                    profile_value DESC,
                    updated_at ASC
                )
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                ranking_server_profile_value_idx
                ON ranking_entries (
                    server,
                    profile_value DESC,
                    updated_at ASC
                )
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                scored_profile_value_idx
                ON scored_profiles (
                    profile_value DESC
                )
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                scored_server_profile_value_idx
                ON scored_profiles (
                    server,
                    profile_value DESC
                )
                """
            )


            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                ranking_rank_name_idx
                ON ranking_entries (rank_name)
                WHERE profile_value > 0
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                ranking_server_rank_name_idx
                ON ranking_entries (
                    server,
                    rank_name
                )
                WHERE profile_value > 0
                """
            )

        connection.commit()


def save_or_update_player(
    uid,
    nickname,
    icon_url,
    profile_value,
    total_score,
    rank_name,
    achievements,
    theater_act,
    theater_stars,
    friendship_count,
    abyss_stars,
    stygian_difficulty,
    stygian_clear_time,
    server="unknown",
):
    """
    公開ランキングへプレイヤーを登録する。

    未登録なら新規登録し、
    登録済みなら最新情報へ更新する。
    """

    updated_at = datetime.now().astimezone()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ranking_entries (
                    uid,
                    nickname,
                    icon_url,
                    profile_value,
                    total_score,
                    rank_name,
                    achievements,
                    theater_act,
                    theater_stars,
                    friendship_count,
                    abyss_stars,
                    stygian_difficulty,
                    stygian_clear_time,
                    server,
                    updated_at
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                ON CONFLICT (uid) DO UPDATE SET
                    nickname = EXCLUDED.nickname,
                    icon_url = EXCLUDED.icon_url,
                    profile_value = EXCLUDED.profile_value,
                    total_score = EXCLUDED.total_score,
                    rank_name = EXCLUDED.rank_name,
                    achievements = EXCLUDED.achievements,
                    theater_act = EXCLUDED.theater_act,
                    theater_stars = EXCLUDED.theater_stars,
                    friendship_count = EXCLUDED.friendship_count,
                    abyss_stars = EXCLUDED.abyss_stars,
                    stygian_difficulty = EXCLUDED.stygian_difficulty,
                    stygian_clear_time = EXCLUDED.stygian_clear_time,
                    server = EXCLUDED.server,
                    updated_at = EXCLUDED.updated_at
                """,
                (
                    int(uid),
                    str(nickname),
                    icon_url,
                    int(profile_value),
                    int(total_score),
                    str(rank_name),
                    int(achievements),
                    int(theater_act),
                    int(theater_stars),
                    int(friendship_count),
                    int(abyss_stars),
                    int(stygian_difficulty),
                    int(stygian_clear_time),
                    str(server),
                    updated_at,
                ),
            )

        connection.commit()


def get_ranking(
    limit=100,
    server=None,
):
    """
    プロフィール値が高い順に公開ランキングを取得する。

    server指定時はサーバー別に絞り込む。
    """

    limit = max(1, min(int(limit), 1000))

    with get_connection() as connection:
        with connection.cursor() as cursor:
            if server and server != "global":
                cursor.execute(
                    """
                    SELECT *
                    FROM ranking_entries
                    WHERE
                        profile_value > 0
                        AND server = %s
                    ORDER BY
                        profile_value DESC,
                        updated_at ASC
                    LIMIT %s
                    """,
                    (
                        str(server),
                        limit,
                    ),
                )
            else:
                cursor.execute(
                    """
                    SELECT *
                    FROM ranking_entries
                    WHERE profile_value > 0
                    ORDER BY
                        profile_value DESC,
                        updated_at ASC
                    LIMIT %s
                    """,
                    (limit,),
                )

            rows = cursor.fetchall()

    return list(rows)


def get_player(uid):
    """
    指定UIDの公開ランキング登録情報を取得する。
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM ranking_entries
                WHERE uid = %s
                """,
                (int(uid),),
            )

            row = cursor.fetchone()

    return row


def get_player_position(
    uid,
    server=None,
):
    """
    指定UIDの公開ランキング順位を1回のSQLで取得する。

    server指定時は、そのプレイヤーが同じサーバーに
    登録されている場合だけサーバー内順位を返す。
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            if server and server != "global":
                cursor.execute(
                    """
                    SELECT
                        CASE
                            WHEN
                                target.profile_value > 0
                                AND target.server = %s
                            THEN (
                                SELECT COUNT(*) + 1
                                FROM ranking_entries AS ranked
                                WHERE
                                    ranked.profile_value
                                        > target.profile_value
                                    AND ranked.server = %s
                            )
                            ELSE NULL
                        END AS position
                    FROM ranking_entries AS target
                    WHERE target.uid = %s
                    """,
                    (
                        str(server),
                        str(server),
                        int(uid),
                    ),
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        CASE
                            WHEN target.profile_value > 0
                            THEN (
                                SELECT COUNT(*) + 1
                                FROM ranking_entries AS ranked
                                WHERE
                                    ranked.profile_value
                                        > target.profile_value
                            )
                            ELSE NULL
                        END AS position
                    FROM ranking_entries AS target
                    WHERE target.uid = %s
                    """,
                    (int(uid),),
                )

            row = cursor.fetchone()

    if not row:
        return None

    position = row.get("position")

    if position is None:
        return None

    return int(position)


def get_ranking_count(
    server=None,
):
    """
    公開ランキング登録人数を取得する。

    server指定時はサーバー別人数を返す。
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            if server and server != "global":
                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM ranking_entries
                    WHERE
                        profile_value > 0
                        AND server = %s
                    """,
                    (str(server),),
                )
            else:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM ranking_entries
                    WHERE profile_value > 0
                    """
                )

            row = cursor.fetchone()

    return int(row["total"])


def save_scored_profile(
    uid,
    profile_value,
    total_score,
    rank_name,
    server,
):
    """
    採点したUIDを母数用テーブルへ保存する。

    すでに存在する場合は最新情報へ更新する。
    """

    updated_at = datetime.now().astimezone()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO scored_profiles (
                    uid,
                    profile_value,
                    total_score,
                    rank_name,
                    server,
                    updated_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                ON CONFLICT (uid) DO UPDATE SET
                    profile_value = EXCLUDED.profile_value,
                    total_score = EXCLUDED.total_score,
                    rank_name = EXCLUDED.rank_name,
                    server = EXCLUDED.server,
                    updated_at = EXCLUDED.updated_at
                """,
                (
                    int(uid),
                    int(profile_value),
                    int(total_score),
                    str(rank_name),
                    str(server),
                    updated_at,
                ),
            )

        connection.commit()


def get_scored_count(
    server=None,
):
    """
    採点済みUIDの人数を取得する。

    server指定時はサーバー別人数を返す。
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            if server and server != "global":
                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM scored_profiles
                    WHERE server = %s
                    """,
                    (str(server),),
                )
            else:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM scored_profiles
                    """
                )

            row = cursor.fetchone()

    return int(row["total"])


def get_scored_position(
    uid,
    server=None,
):
    """
    採点済みUID全体での順位を1回のSQLで取得する。

    server指定時は、そのUIDが同じサーバーに
    保存されている場合だけサーバー内順位を返す。
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            if server and server != "global":
                cursor.execute(
                    """
                    SELECT
                        CASE
                            WHEN target.server = %s
                            THEN (
                                SELECT COUNT(*) + 1
                                FROM scored_profiles AS scored
                                WHERE
                                    scored.profile_value
                                        > target.profile_value
                                    AND scored.server = %s
                            )
                            ELSE NULL
                        END AS position
                    FROM scored_profiles AS target
                    WHERE target.uid = %s
                    """,
                    (
                        str(server),
                        str(server),
                        int(uid),
                    ),
                )
            else:
                cursor.execute(
                    """
                    SELECT (
                        SELECT COUNT(*) + 1
                        FROM scored_profiles AS scored
                        WHERE
                            scored.profile_value
                                > target.profile_value
                    ) AS position
                    FROM scored_profiles AS target
                    WHERE target.uid = %s
                    """,
                    (int(uid),),
                )

            row = cursor.fetchone()

    if not row:
        return None

    position = row.get("position")

    if position is None:
        return None

    return int(position)

def get_scored_rank_summary(
    uid,
    server=None,
):
    """
    採点済みUID全体での順位・母数・上位割合を
    1回のSQLで取得する。

    server指定時はサーバー別で集計する。
    serverがNoneまたは"global"の場合は全体集計。
    """

    uid = int(uid)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            if server and server != "global":
                cursor.execute(
                    """
                    SELECT
                        target.uid,
                        (
                            SELECT COUNT(*) + 1
                            FROM scored_profiles AS ranked
                            WHERE
                                ranked.profile_value
                                    > target.profile_value
                                AND ranked.server = %s
                        ) AS position,
                        (
                            SELECT COUNT(*)
                            FROM scored_profiles
                            WHERE server = %s
                        ) AS total
                    FROM scored_profiles AS target
                    WHERE
                        target.uid = %s
                        AND target.server = %s
                    """,
                    (
                        str(server),
                        str(server),
                        uid,
                        str(server),
                    ),
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        target.uid,
                        (
                            SELECT COUNT(*) + 1
                            FROM scored_profiles AS ranked
                            WHERE
                                ranked.profile_value
                                    > target.profile_value
                        ) AS position,
                        (
                            SELECT COUNT(*)
                            FROM scored_profiles
                        ) AS total
                    FROM scored_profiles AS target
                    WHERE target.uid = %s
                    """,
                    (uid,),
                )

            row = cursor.fetchone()

    if not row:
        return {
            "position": None,
            "total": 0,
            "top_percent": None,
        }

    position = int(row["position"])
    total = int(row["total"])

    if total <= 0:
        top_percent = None
    else:
        top_percent = round(
            position / total * 100,
            1,
        )

    return {
        "position": position,
        "total": total,
        "top_percent": top_percent,
    }

def get_statistics(
    server="global",
):
    """
    統計ページ用データをDBとの1往復で取得する。

    ranking_entriesとscored_profilesの両方を対象にし、
    同じUIDは1人として統合する。

    同じUIDが両方のテーブルに存在する場合:
    1. updated_atが新しいデータを優先
    2. updated_atが同じ場合はscored_profilesを優先

    取得内容:
    - 統合後の人数
    - 平均プロフィール値
    - 中央プロフィール値
    - 最高プロフィール値
    - 平均スコア
    - 最高スコア
    - ランク帯分布
    - サーバー別人数

    serverが"global"の場合は全体集計。
    それ以外は指定サーバー内だけを集計する。
    """

    selected_server = str(
        server or "global"
    ).strip().lower()

    allowed_servers = {
        "global",
        "asia",
        "america",
        "europe",
        "tw",
        "cn",
        "unknown",
    }

    if selected_server not in allowed_servers:
        selected_server = "global"

    rank_order = [
        "SSS",
        "SS+",
        "SS",
        "S+",
        "S",
        "A+",
        "A",
        "B+",
        "B",
        "C",
        "D",
    ]

    server_order = [
        "asia",
        "america",
        "europe",
        "tw",
        "cn",
        "unknown",
    ]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                WITH combined_source AS (
                    SELECT
                        uid,
                        profile_value,
                        total_score,
                        rank_name,
                        server,
                        updated_at,
                        1 AS source_priority
                    FROM ranking_entries

                    UNION ALL

                    SELECT
                        uid,
                        profile_value,
                        total_score,
                        rank_name,
                        server,
                        updated_at,
                        2 AS source_priority
                    FROM scored_profiles
                ),
                combined_profiles AS (
                    SELECT DISTINCT ON (uid)
                        uid,
                        profile_value,
                        total_score,
                        rank_name,
                        server,
                        updated_at
                    FROM combined_source
                    ORDER BY
                        uid,
                        updated_at DESC,
                        source_priority DESC
                ),
                filtered AS (
                    SELECT
                        profile_value,
                        total_score,
                        rank_name
                    FROM combined_profiles
                    WHERE
                        (
                            %s = 'global'
                            OR server = %s
                        )
                ),
                summary AS (
                    SELECT
                        COUNT(*)::BIGINT AS total_players,
                        COALESCE(
                            ROUND(AVG(profile_value)),
                            0
                        )::BIGINT AS average_profile_value,
                        COALESCE(
                            ROUND(
                                PERCENTILE_CONT(0.5)
                                WITHIN GROUP (
                                    ORDER BY profile_value
                                )
                            ),
                            0
                        )::BIGINT AS median_profile_value,
                        COALESCE(
                            MAX(profile_value),
                            0
                        )::BIGINT AS highest_profile_value,
                        COALESCE(
                            ROUND(
                                AVG(total_score)::NUMERIC,
                                1
                            ),
                            0
                        ) AS average_total_score,
                        COALESCE(
                            MAX(total_score),
                            0
                        )::BIGINT AS highest_total_score
                    FROM filtered
                ),
                rank_counts AS (
                    SELECT
                        rank_name,
                        COUNT(*)::BIGINT AS player_count
                    FROM filtered
                    GROUP BY rank_name
                ),
                server_counts AS (
                    SELECT
                        server,
                        COUNT(*)::BIGINT AS player_count
                    FROM combined_profiles
                    GROUP BY server
                )
                SELECT
                    summary.total_players,
                    summary.average_profile_value,
                    summary.median_profile_value,
                    summary.highest_profile_value,
                    summary.average_total_score,
                    summary.highest_total_score,
                    COALESCE(
                        (
                            SELECT JSONB_OBJECT_AGG(
                                rank_name,
                                player_count
                            )
                            FROM rank_counts
                        ),
                        '{}'::JSONB
                    ) AS rank_counts,
                    COALESCE(
                        (
                            SELECT JSONB_OBJECT_AGG(
                                server,
                                player_count
                            )
                            FROM server_counts
                        ),
                        '{}'::JSONB
                    ) AS server_counts
                FROM summary
                """,
                (
                    selected_server,
                    selected_server,
                ),
            )

            row = cursor.fetchone()

    if not row:
        row = {
            "total_players": 0,
            "average_profile_value": 0,
            "median_profile_value": 0,
            "highest_profile_value": 0,
            "average_total_score": 0,
            "highest_total_score": 0,
            "rank_counts": {},
            "server_counts": {},
        }

    rank_counts_raw = row.get(
        "rank_counts"
    ) or {}

    server_counts_raw = row.get(
        "server_counts"
    ) or {}

    rank_counts = {
        str(rank): int(count)
        for rank, count in rank_counts_raw.items()
    }

    server_counts = {
        str(server_name): int(count)
        for server_name, count
        in server_counts_raw.items()
    }

    total_players = int(
        row.get("total_players") or 0
    )

    rank_distribution = []

    for rank in rank_order:
        count = rank_counts.get(
            rank,
            0,
        )

        percentage = (
            round(
                count
                / total_players
                * 100,
                1,
            )
            if total_players > 0
            else 0.0
        )

        rank_distribution.append(
            {
                "rank": rank,
                "count": count,
                "percentage": percentage,
            }
        )

    known_ranks = set(rank_order)

    for rank in sorted(
        name
        for name in rank_counts
        if name not in known_ranks
    ):
        count = rank_counts[rank]

        percentage = (
            round(
                count
                / total_players
                * 100,
                1,
            )
            if total_players > 0
            else 0.0
        )

        rank_distribution.append(
            {
                "rank": rank,
                "count": count,
                "percentage": percentage,
            }
        )

    global_server_total = sum(
        server_counts.values()
    )

    server_distribution = []

    for server_name in server_order:
        count = server_counts.get(
            server_name,
            0,
        )

        percentage = (
            round(
                count
                / global_server_total
                * 100,
                1,
            )
            if global_server_total > 0
            else 0.0
        )

        server_distribution.append(
            {
                "server": server_name,
                "count": count,
                "percentage": percentage,
            }
        )

    known_servers = set(server_order)

    for server_name in sorted(
        name
        for name in server_counts
        if name not in known_servers
    ):
        count = server_counts[
            server_name
        ]

        percentage = (
            round(
                count
                / global_server_total
                * 100,
                1,
            )
            if global_server_total > 0
            else 0.0
        )

        server_distribution.append(
            {
                "server": server_name,
                "count": count,
                "percentage": percentage,
            }
        )

    return {
        "selected_server": selected_server,
        "total_players": total_players,
        "average_profile_value": int(
            row.get(
                "average_profile_value"
            ) or 0
        ),
        "median_profile_value": int(
            row.get(
                "median_profile_value"
            ) or 0
        ),
        "highest_profile_value": int(
            row.get(
                "highest_profile_value"
            ) or 0
        ),
        "average_total_score": float(
            row.get(
                "average_total_score"
            ) or 0
        ),
        "highest_total_score": int(
            row.get(
                "highest_total_score"
            ) or 0
        ),
        "rank_distribution": (
            rank_distribution
        ),
        "server_distribution": (
            server_distribution
        ),
    }