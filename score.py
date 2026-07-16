# score.py

THEORY_ACHIEVEMENT = 1757
THEORY_FRIENDSHIP_COUNT = 115

THEORY_THEATER_ACT = 10
THEORY_THEATER_STARS = 12

THEORY_STYGIAN_CLEAR_TIME = 54
THEORY_STYGIAN_POINT = 1800

THEORY_ABYSS_STARS = 36


def to_int(value) -> int:
    """Noneや文字列を安全に整数へ変換する。"""

    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


# ======================
# 幽境の激戦ポイント
# ======================
def calculate_stygian_point(
    difficulty,
    clear_time,
) -> int:
    difficulty = to_int(difficulty)
    clear_time = to_int(clear_time)

    if difficulty >= 6:
        if 0 < clear_time <= 180:
            return 1800

        return 1600

    elif difficulty == 5:
        return 1200

    elif difficulty == 4:
        return 800

    elif difficulty == 3:
        return 400

    return 0


# ======================
# プロフィール値
# ======================
def calculate_profile_value(
    achievements,
    theater_act,
    theater_stars,
    friendship_count,
    abyss_stars,
    stygian_difficulty,
    stygian_clear_time,
) -> int:
    achievements = to_int(achievements)
    theater_act = to_int(theater_act)
    theater_stars = to_int(theater_stars)
    friendship_count = to_int(friendship_count)
    abyss_stars = to_int(abyss_stars)
    stygian_difficulty = to_int(stygian_difficulty)
    stygian_clear_time = to_int(stygian_clear_time)

    theater_value = (
        10
        * theater_act
        * theater_stars
    )

    friendship_value = friendship_count * 10

    if stygian_clear_time > 0:
        stygian_time_value = max(
            360 - stygian_clear_time,
            0,
        )
    else:
        stygian_time_value = 0

    stygian_point = calculate_stygian_point(
        stygian_difficulty,
        stygian_clear_time,
    )

    base_value = (
        achievements
        + theater_value
        + friendship_value
        + stygian_time_value
        + stygian_point
    )

    return base_value * abyss_stars


# ======================
# 理論プロフィール値
# ======================
THEORETICAL_PROFILE_VALUE = (
    (
        THEORY_ACHIEVEMENT
        + (
            10
            * THEORY_THEATER_ACT
            * THEORY_THEATER_STARS
        )
        + THEORY_FRIENDSHIP_COUNT * 10
        + (
            360
            - THEORY_STYGIAN_CLEAR_TIME
        )
        + THEORY_STYGIAN_POINT
    )
    * THEORY_ABYSS_STARS
)


# ======================
# 100点満点への換算
# ======================
def calculate_total_score(
    profile_value,
) -> int:
    """
    理論プロフィール値を100点として換算する。
    """

    profile_value = to_int(profile_value)

    if THEORETICAL_PROFILE_VALUE <= 0:
        return 0

    score = (
        profile_value
        / THEORETICAL_PROFILE_VALUE
        * 100
    )

    return min(round(score), 100)


# ======================
# 総合ランク
# ======================
def rank_name(total: int) -> str:
    if total >= 95:
        return "SSS"
    elif total >= 90:
        return "SS+"
    elif total >= 85:
        return "SS"
    elif total >= 80:
        return "S"
    elif total >= 70:
        return "A+"
    elif total >= 60:
        return "A"
    elif total >= 50:
        return "B"
    elif total >= 35:
        return "C"
    else:
        return "D"