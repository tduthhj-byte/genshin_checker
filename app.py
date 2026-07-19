import time

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
)

from database import (
    create_table,
    get_player,
    get_player_position,
    get_ranking,
    get_ranking_count,
    get_scored_position,
    save_or_update_player,
    save_scored_profile,
)

from enka_api import get_profile
from lang import get_texts
from score import (
    ACHIEVEMENT_FULL_SCORE_COUNT,
    FRIENDSHIP_MULTIPLIER,
    MAX_TOTAL_SCORE,
    THEORETICAL_PROFILE_VALUE,
    THEORY_ACHIEVEMENT,
    THEORY_FRIENDSHIP_COUNT,
    calculate_profile_value,
    calculate_stygian_point,
    calculate_total_score,
    get_stygian_multiplier,
    rank_name,
    score_abyss,
    score_achievement,
    score_ar,
    score_friendship,
    score_stygian,
    score_theater,
)

app = Flask(__name__)
RANKING_COUNT_CACHE = {
    "value": 0,
    "expires_at": 0,
}


def get_cached_ranking_count():
    """ランキング登録人数を10分間保存して再利用する。"""

    now = time.time()

    if now < RANKING_COUNT_CACHE["expires_at"]:
        return RANKING_COUNT_CACHE["value"]

    count = get_ranking_count()

    RANKING_COUNT_CACHE["value"] = count
    RANKING_COUNT_CACHE["expires_at"] = now + 600

    return count


def clear_ranking_count_cache():
    """ランキング登録後に人数キャッシュをリセットする。"""

    RANKING_COUNT_CACHE["expires_at"] = 0

# create_table()


def get_language(source="args"):
    """GETまたはPOSTから表示言語を取得する。"""

    if source == "form":
        language = request.form.get("lang", "ja")
    else:
        language = request.args.get("lang", "ja")

    language = str(language).strip().lower()

    if language not in {"ja", "en", "zh"}:
        language = "ja"

    return language


def difficulty_to_roman(difficulty):
    """幽境の激戦の難易度をローマ数字へ変換する。"""

    table = {
        1: "I",
        2: "II",
        3: "III",
        4: "IV",
        5: "V",
        6: "VI",
    }

    try:
        number = int(difficulty)

        if number <= 0:
            return "未挑戦"

        return table.get(number, str(number))

    except (TypeError, ValueError):
        return "未挑戦"


def get_icon_url(player):
    """プロフィール画像URLを安全に取得する。"""

    if not player.profile_picture_icon:
        return None

    return player.profile_picture_icon.circle


def detect_server(uid):
    """UIDからサーバーを判定する。"""

    uid_text = str(uid)

    if uid_text.startswith("18"):
        return "asia"
    if uid_text.startswith("6"):
        return "america"
    if uid_text.startswith("7"):
        return "europe"
    if uid_text.startswith("8"):
        return "asia"
    if uid_text.startswith("9"):
        return "tw"
    if uid_text.startswith(("1", "2", "3", "5")):
        return "cn"

    return "unknown"


def calculate_player_data(uid):
    """Enkaからプロフィールを取得し、採点用データを計算する。"""

    showcase = get_profile(uid)
    player = showcase.player

    ar = player.level or 0
    achievements = player.achievements or 0
    abyss_stars = player.abyss_stars or 0
    theater_act = player.theater_act or 0
    theater_stars = player.theater_stars or 0
    stygian_difficulty = player.stygian_difficulty or 0
    stygian_clear_time = player.stygian_clear_time or 0
    friendship_count = player.max_friendship_character_count or 0
    icon_url = get_icon_url(player)

    theater_value = 10 * theater_act * theater_stars
    friendship_value = friendship_count * FRIENDSHIP_MULTIPLIER

    if stygian_clear_time > 0:
        stygian_time_value = max(360 - stygian_clear_time, 0)
    else:
        stygian_time_value = 0

    raw_stygian_point = calculate_stygian_point(
        stygian_difficulty,
        stygian_clear_time,
    )
    stygian_multiplier = get_stygian_multiplier()
    stygian_scaled_point = round(
        raw_stygian_point * stygian_multiplier
    )
    stygian_total_value = (
        stygian_time_value + stygian_scaled_point
    )
    abyss_multiplier = max(abyss_stars - 35, 0)

    profile_value = calculate_profile_value(
        achievements=achievements,
        theater_act=theater_act,
        theater_stars=theater_stars,
        friendship_count=friendship_count,
        abyss_stars=abyss_stars,
        stygian_difficulty=stygian_difficulty,
        stygian_clear_time=stygian_clear_time,
    )

    achievement_score = score_achievement(achievements)
    theater_score = score_theater(
        theater_act,
        theater_stars,
    )
    stygian_score = score_stygian(
        stygian_difficulty,
        stygian_clear_time,
    )
    abyss_score = score_abyss(abyss_stars)
    friendship_score = score_friendship(friendship_count)
    ar_score = score_ar(ar)

    total = calculate_total_score(
        achievement_score=achievement_score,
        theater_score=theater_score,
        stygian_score=stygian_score,
        abyss_score=abyss_score,
        friendship_score=friendship_score,
        ar_score=ar_score,
    )
    rank_result = rank_name(total)

    if THEORY_ACHIEVEMENT > 0:
        achievement_rate = (
            achievements / THEORY_ACHIEVEMENT * 100
        )
    else:
        achievement_rate = 0

    if ACHIEVEMENT_FULL_SCORE_COUNT > 0:
        achievement_score_rate = (
            achievements
            / ACHIEVEMENT_FULL_SCORE_COUNT
            * 100
        )
    else:
        achievement_score_rate = 0

    stygian_roman = difficulty_to_roman(
        stygian_difficulty
    )

    return {
        "player": player,
        "uid": uid,
        "total": total,
        "max_total_score": MAX_TOTAL_SCORE,
        "rank": rank_result,
        "profile_value": profile_value,
        "theoretical_profile_value": THEORETICAL_PROFILE_VALUE,
        "achievements": achievements,
        "theory_achievement": THEORY_ACHIEVEMENT,
        "achievement_full_score_count": ACHIEVEMENT_FULL_SCORE_COUNT,
        "achievement_rate": achievement_rate,
        "achievement_score_rate": achievement_score_rate,
        "achievement_score": achievement_score,
        "theater_act": theater_act,
        "theater_stars": theater_stars,
        "theater_value": theater_value,
        "theater_score": theater_score,
        "stygian_difficulty": stygian_difficulty,
        "stygian_roman": stygian_roman,
        "stygian_clear_time": stygian_clear_time,
        "raw_stygian_point": raw_stygian_point,
        "stygian_multiplier": stygian_multiplier,
        "stygian_scaled_point": stygian_scaled_point,
        "stygian_time_value": stygian_time_value,
        "stygian_total_value": stygian_total_value,
        "stygian_score": stygian_score,
        "abyss_stars": abyss_stars,
        "abyss_multiplier": abyss_multiplier,
        "abyss_score": abyss_score,
        "friendship_count": friendship_count,
        "theory_friendship_count": THEORY_FRIENDSHIP_COUNT,
        "friendship_multiplier": FRIENDSHIP_MULTIPLIER,
        "friendship_value": friendship_value,
        "friendship_score": friendship_score,
        "ar": ar,
        "ar_score": ar_score,
        "icon_url": icon_url,
    }


@app.route("/")
def home():
    language = get_language()
    texts = get_texts(language)

    return render_template(
        "index.html",
        language=language,
        texts=texts,
        ranking_count = get_cached_ranking_count(),
        ranking_error=request.args.get(
            "ranking_error",
            "",
        ).strip(),
    )


@app.route("/criteria")
def criteria():
    language = get_language()
    texts = get_texts(language)

    return render_template(
        "criteria.html",
        language=language,
        texts=texts,
        theory_achievement=THEORY_ACHIEVEMENT,
        achievement_full_score_count=ACHIEVEMENT_FULL_SCORE_COUNT,
        theory_friendship_count=THEORY_FRIENDSHIP_COUNT,
        theoretical_profile_value=THEORETICAL_PROFILE_VALUE,
        max_total_score=MAX_TOTAL_SCORE,
        friendship_multiplier=FRIENDSHIP_MULTIPLIER,
        stygian_multiplier=get_stygian_multiplier(),
    )


@app.route("/rank")
def rank():
    language = get_language()
    texts = get_texts(language)

    uid_text = request.args.get("uid", "").strip()
    ranking_registered = (
        request.args.get("ranking_registered") == "1"
    )
    ranking_position = request.args.get(
        "ranking_position",
        "",
    ).strip()
    ranking_error = request.args.get(
        "ranking_error",
        "",
    ).strip()

    if not uid_text.isdigit():
        return render_template(
            "index.html",
            language=language,
            texts=texts,
            error=texts.get(
                "uid_numeric_error",
                "UIDは数字で入力してください。",
            ),
            entered_uid=uid_text,
            ranking_count=get_cached_ranking_count(),
        )

    if len(uid_text) not in (9, 10):
        return render_template(
            "index.html",
            language=language,
            texts=texts,
            error=texts.get(
                "uid_length_error",
                "UIDは9桁または10桁で入力してください。",
            ),
            entered_uid=uid_text,
            ranking_count=get_cached_ranking_count(),
        )

    uid = int(uid_text)

    try:
        player_data = calculate_player_data(uid)

        save_scored_profile(
            uid=uid,
            profile_value=player_data["profile_value"],
            total_score=player_data["total"],
            rank_name=player_data["rank"],
            server=detect_server(uid),
        )

        registered_player = get_player(uid)
        ranking_position = get_scored_position(
            uid,
            server=detect_server(uid),
        )

        player_data.update(
    {
        "language": language,
        "texts": texts,
        "ranking_registered": ranking_registered,
        "ranking_position": ranking_position,
        "ranking_error": ranking_error,
        "is_ranking_registered": (
            registered_player is not None
        ),
    }
)

        return render_template(
            "result.html",
            **player_data,
        )

    except Exception as error:
        print(
            "プロフィール取得エラー: "
            f"{type(error).__name__}: {error}"
        )

        return render_template(
            "index.html",
            language=language,
            texts=texts,
            error=texts.get(
                "profile_fetch_error",
                (
                    "プロフィールを取得できませんでした。"
                    "UID、ゲーム内プロフィールの公開設定、"
                    "Enka.Networkの状態を確認してください。"
                ),
            ),
            entered_uid=uid_text,
            ranking_count=get_cached_ranking_count(),
        )


@app.route(
    "/ranking/register",
    methods=["POST"],
)
def register_ranking():
    """最新情報でランキングへ登録・更新する。"""

    language = get_language(source="form")
    texts = get_texts(language)
    uid_text = request.form.get("uid", "").strip()

    if not uid_text.isdigit():
        return redirect(
            url_for(
                "home",
                lang=language,
                ranking_error=texts.get(
                    "ranking_invalid_uid_error",
                    "ランキング登録用UIDが正しくありません。",
                ),
            )
        )

    if len(uid_text) not in (9, 10):
        return redirect(
            url_for(
                "home",
                lang=language,
                ranking_error=texts.get(
                    "uid_length_error",
                    "UIDは9桁または10桁で入力してください。",
                ),
            )
        )

    uid = int(uid_text)

    try:
        player_data = calculate_player_data(uid)
        profile_value = player_data["profile_value"]

        if profile_value <= 0:
            return redirect(
                url_for(
                    "rank",
                    uid=uid,
                    lang=language,
                    ranking_error=texts.get(
                        "ranking_profile_zero_error",
                        (
                            "プロフィール値が0のため、"
                            "ランキングへ登録できません。"
                        ),
                    ),
                )
            )

        player = player_data["player"]
        server = detect_server(uid)

        save_or_update_player(
            uid=uid,
            nickname=player.nickname,
            icon_url=player_data["icon_url"],
            profile_value=profile_value,
            total_score=player_data["total"],
            rank_name=player_data["rank"],
            achievements=player_data["achievements"],
            theater_act=player_data["theater_act"],
            theater_stars=player_data["theater_stars"],
            friendship_count=player_data["friendship_count"],
            abyss_stars=player_data["abyss_stars"],
            stygian_difficulty=player_data["stygian_difficulty"],
            stygian_clear_time=player_data["stygian_clear_time"],
            server=server,
        )

        clear_ranking_count_cache()

        position = get_scored_position(
            uid,
            server=server,
        )

        return redirect(
            url_for(
                "ranking",
                lang=language,
                server=server,
                player_uid=uid,
                registered=1,
            )
        )

    except Exception as error:
        print(
            "ランキング登録エラー: "
            f"{type(error).__name__}: {error}"
        )

        return redirect(
            url_for(
                "rank",
                uid=uid,
                lang=language,
                ranking_error=texts.get(
                    "ranking_registration_error",
                    (
                        "ランキング登録に失敗しました。"
                        "時間を置いて再度お試しください。"
                    ),
                ),
            )
        )


@app.route("/ranking")
def ranking():
    language = get_language()
    texts = get_texts(language)

    player_uid_text = request.args.get(
        "player_uid",
        "",
    ).strip()

    current_player = None
    current_position = None

    selected_server = request.args.get(
        "server",
        "global",
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

    if player_uid_text.isdigit():
        player_uid = int(player_uid_text)

        current_player = get_player(
            player_uid
        )

        if current_player:
            current_position = get_player_position(
                player_uid,
                server=selected_server,
            )

    entries = get_ranking(
        limit=100,
        server=selected_server,
    )

    ranking_count = get_ranking_count(
        server=selected_server,
    )

    ranking_entries = []

    for position, entry in enumerate(
        entries,
        start=1,
    ):
        entry["position"] = position
        uid_text = str(entry["uid"])

        if len(uid_text) >= 6:
            entry["masked_uid"] = (
                uid_text[:3]
                + "*" * (len(uid_text) - 6)
                + uid_text[-3:]
            )
        else:
            entry["masked_uid"] = uid_text

        updated_at = entry.get("updated_at")

        if hasattr(updated_at, "strftime"):
            entry["updated_at_text"] = (
                updated_at.strftime("%Y-%m-%d")
            )
        else:
            entry["updated_at_text"] = str(
                updated_at or ""
            )[:10]

        ranking_entries.append(entry)

    server_labels = {
        "global": "Global",
        "asia": "Asia",
        "america": "America",
        "europe": "Europe",
        "tw": "TW / HK / MO",
        "cn": "China",
        "unknown": "Unknown",
    }

    return render_template(
        "ranking.html",
        language=language,
        texts=texts,
        ranking_entries=ranking_entries,
        ranking_count=ranking_count,
        selected_server=selected_server,
        selected_server_label=server_labels[
            selected_server
        ],
        current_player=current_player,
        current_position=current_position,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )