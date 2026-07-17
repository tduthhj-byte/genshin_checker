import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "ranking.db"


def get_connection():
    """SQLiteデータベースへ接続する。"""

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    """ランキング用テーブルを作成する。"""

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ranking_entries (
                uid INTEGER PRIMARY KEY,
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
                updated_at TEXT NOT NULL
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
):
    """
    未登録なら新規登録し、
    登録済みなら最新情報へ更新する。
    """

    updated_at = datetime.now().isoformat(
        timespec="seconds"
    )

    with get_connection() as connection:
        connection.execute(
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
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(uid) DO UPDATE SET
                nickname = excluded.nickname,
                icon_url = excluded.icon_url,
                profile_value = excluded.profile_value,
                total_score = excluded.total_score,
                rank_name = excluded.rank_name,
                achievements = excluded.achievements,
                theater_act = excluded.theater_act,
                theater_stars = excluded.theater_stars,
                friendship_count = excluded.friendship_count,
                abyss_stars = excluded.abyss_stars,
                stygian_difficulty = excluded.stygian_difficulty,
                stygian_clear_time = excluded.stygian_clear_time,
                updated_at = excluded.updated_at
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
                updated_at,
            ),
        )

        connection.commit()


def get_ranking(limit=100):
    """プロフィール値が高い順にランキングを取得する。"""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM ranking_entries
            WHERE profile_value > 0
            ORDER BY
                profile_value DESC,
                updated_at ASC
            LIMIT ?
            """,
            (int(limit),),
        ).fetchall()

    return [dict(row) for row in rows]


def get_player(uid):
    """指定UIDの登録情報を取得する。"""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM ranking_entries
            WHERE uid = ?
            """,
            (int(uid),),
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def get_player_position(uid):
    """指定UIDの現在順位を取得する。"""

    player = get_player(uid)

    if not player:
        return None

    profile_value = int(player["profile_value"])

    if profile_value <= 0:
        return None

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) + 1 AS position
            FROM ranking_entries
            WHERE profile_value > ?
            """,
            (profile_value,),
        ).fetchone()

    return int(row["position"])


def get_ranking_count():
    """ランキング登録人数を取得する。"""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM ranking_entries
            WHERE profile_value > 0
            """
        ).fetchone()

    return int(row["total"])