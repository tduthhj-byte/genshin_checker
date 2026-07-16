from flask import Flask, render_template, request

from enka_api import get_profile
from score import (
    THEORETICAL_PROFILE_VALUE,
    THEORY_ACHIEVEMENT,
    calculate_profile_value,
    calculate_total_score,
    rank_name,
)

app = Flask(__name__)


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
        return table.get(number, str(difficulty))

    except (TypeError, ValueError):
        if difficulty is None:
            return "未挑戦"

        return str(difficulty)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/criteria")
def criteria():
    return render_template(
        "criteria.html",
        theory_achievement=THEORY_ACHIEVEMENT,
    )


@app.route("/rank")
def rank():
    uid_text = request.args.get("uid", "").strip()

    if not uid_text.isdigit():
        return render_template(
            "index.html",
            error="UIDは数字で入力してください。",
            entered_uid=uid_text,
        )

    if len(uid_text) not in (9, 10):
        return render_template(
            "index.html",
            error="UIDは9桁または10桁で入力してください。",
            entered_uid=uid_text,
        )

    uid = int(uid_text)

    try:
        showcase = get_profile(uid)
        player = showcase.player

        achievements = player.achievements or 0
        abyss_stars = player.abyss_stars or 0
        theater_act = player.theater_act or 0
        theater_stars = player.theater_stars or 0
        stygian_difficulty = player.stygian_difficulty or 0
        stygian_clear_time = player.stygian_clear_time or 0

        friendship_count = (
            player.max_friendship_character_count or 0
        )

        # Enkaでは幽境の挑戦回数を取得できないため0にする
        stygian_count = 0

        profile_value = calculate_profile_value(
            achievements=achievements,
            theater_act=theater_act,
            theater_stars=theater_stars,
            friendship_count=friendship_count,
            abyss_stars=abyss_stars,
            stygian_difficulty=stygian_difficulty,
            stygian_clear_time=stygian_clear_time,
        )

        total = calculate_total_score(profile_value)

        rank_result = rank_name(total)

        if THEORY_ACHIEVEMENT > 0:
            achievement_rate = (
                achievements / THEORY_ACHIEVEMENT * 100
            )
        else:
            achievement_rate = 0

        stygian_roman = difficulty_to_roman(
            stygian_difficulty
        )

        icon_url = None

        if player.profile_picture_icon:
            icon_url = player.profile_picture_icon.circle

        return render_template(
            "result.html",
            player=player,
            uid=uid,
            total=total,
            rank=rank_result,
            profile_value=profile_value,
            friendship_count=friendship_count,
            theory_achievement=THEORY_ACHIEVEMENT,
            achievement_rate=achievement_rate,
            stygian_difficulty=stygian_difficulty,
            stygian_roman=stygian_roman,
            stygian_clear_time=stygian_clear_time,
            icon_url=icon_url,
        )

    except Exception as error:
        print(f"プロフィール取得エラー: {error}")

        return render_template(
            "index.html",
            error=(
                "プロフィールを取得できませんでした。"
                "UID、ゲーム内プロフィールの公開設定、"
                "Enka.Networkの状態を確認してください。"
            ),
            entered_uid=uid_text,
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
