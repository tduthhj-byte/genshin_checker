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
    kwargs={
        "row_factory": dict_row,
    },
    open=True,
)


def get_connection():
    """
    Supabase PostgreSQLの接続プールから
    接続を取得する。

    with文を抜けると接続は切断されず、
    接続プールへ返却される。
    """

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
