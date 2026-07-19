import os
from datetime import datetime

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    """
    Supabase PostgreSQLへ接続する。
    """

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URLが設定されていません。"
        )

    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
    )


def create_table():
    """
    ランキング用テーブルを作成する。
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
                CREATE INDEX IF NOT EXISTS
                ranking_server_profile_value_idx
                ON ranking_entries (
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
    プロフィール値が高い順にランキングを取得する。
    server指定時はサーバー別に絞り込む。
    """

    limit = int(limit)

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
    指定UIDの登録情報を取得する。
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
    指定UIDの現在順位を取得する。
    server指定時はサーバー内順位を返す。
    """

    player = get_player(uid)

    if not player:
        return None

    profile_value = int(
        player["profile_value"]
    )

    if profile_value <= 0:
        return None

    with get_connection() as connection:
        with connection.cursor() as cursor:

            if server and server != "global":
                cursor.execute(
                    """
                    SELECT COUNT(*) + 1 AS position
                    FROM ranking_entries
                    WHERE
                        profile_value > %s
                        AND server = %s
                    """,
                    (
                        profile_value,
                        str(server),
                    ),
                )

            else:
                cursor.execute(
                    """
                    SELECT COUNT(*) + 1 AS position
                    FROM ranking_entries
                    WHERE profile_value > %s
                    """,
                    (profile_value,),
                )

            row = cursor.fetchone()

    return int(row["position"])


def get_ranking_count(
    server=None,
):
    """
    ランキング登録人数を取得する。
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
    採点したUIDを保存する。
    既に存在する場合は最新情報へ更新する。
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
                ON CONFLICT (uid)
                DO UPDATE SET
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


def get_scored_count(server=None):
    """
    採点済み人数を取得する。
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

def get_scored_count(server=None):
    """
    採点済み人数を取得する。
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
    採点済みUID全体での順位を取得する。
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT profile_value
                FROM scored_profiles
                WHERE uid = %s
                """,
                (int(uid),),
            )

            player = cursor.fetchone()

            if not player:
                return None

            profile_value = int(
                player["profile_value"]
            )

            if server and server != "global":
                cursor.execute(
                    """
                    SELECT COUNT(*) + 1 AS position
                    FROM scored_profiles
                    WHERE
                        profile_value > %s
                        AND server = %s
                    """,
                    (
                        profile_value,
                        str(server),
                    ),
                )
            else:
                cursor.execute(
                    """
                    SELECT COUNT(*) + 1 AS position
                    FROM scored_profiles
                    WHERE profile_value > %s
                    """,
                    (profile_value,),
                )

            row = cursor.fetchone()

    return int(row["position"])