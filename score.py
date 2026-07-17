# score.py


# =====================================
# 理論値・採点基準
# =====================================

# 現在取得できるアチーブメント理論値
THEORY_ACHIEVEMENT = 1757

# 通常30点満点となる基準
ACHIEVEMENT_FULL_SCORE_COUNT = 1752

# 好感度MAXキャラの現在の理論人数
THEORY_FRIENDSHIP_COUNT = 116

THEORY_THEATER_ACT = 10
THEORY_THEATER_STARS = 12

THEORY_STYGIAN_CLEAR_TIME = 54
THEORY_STYGIAN_POINT = 1800

THEORY_ABYSS_STARS = 36


# =====================================
# 調整用定数
# =====================================

# 幽境の開催期数
# 第10期 → 10
# 第11期 → 11
STYGIAN_SEASON_COUNT = 10

# プロフィール値での好感度係数
FRIENDSHIP_MULTIPLIER = 5

# 基本点100点＋ボーナス最大10点
BASE_MAX_SCORE = 100
BONUS_MAX_SCORE = 10
MAX_TOTAL_SCORE = 110


def to_int(value) -> int:
    """Noneや文字列を安全に整数へ変換する。"""

    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


# =====================================
# プロフィール値用の計算
# =====================================

def get_stygian_multiplier() -> float:
    """
    幽境開催期数から倍率を計算する。

    第10期：1.10倍
    第11期：1.11倍
    """

    return 1 + STYGIAN_SEASON_COUNT / 100


def calculate_stygian_point(
    difficulty,
    clear_time,
) -> int:
    """プロフィール値に使用する幽境ポイントを計算する。"""

    difficulty = to_int(difficulty)
    clear_time = to_int(clear_time)

    # VI・180秒以内
    if difficulty >= 6:
        if 0 < clear_time <= 180:
            return 1800

        # VIだが180秒以内ではない場合
        return 1600

    if difficulty == 5:
        return 1200

    if difficulty == 4:
        return 800

    if difficulty == 3:
        return 400

    return 0


def calculate_profile_value(
    achievements,
    theater_act,
    theater_stars,
    friendship_count,
    abyss_stars,
    stygian_difficulty,
    stygian_clear_time,
) -> int:
    """
    ランキング用のプロフィール値を計算する。

    [
        アチーブメント
        + 10 × シアター幕数 × 星数
        + 好感度MAX人数 × 5
        + max(360 - 幽境タイム, 0)
        + 幽境ポイント × 開催倍率
    ]
    × max(螺旋星数 - 35, 0)
    """

    achievements = max(to_int(achievements), 0)
    theater_act = max(to_int(theater_act), 0)
    theater_stars = max(to_int(theater_stars), 0)
    friendship_count = max(to_int(friendship_count), 0)
    abyss_stars = max(to_int(abyss_stars), 0)
    stygian_difficulty = max(
        to_int(stygian_difficulty),
        0,
    )
    stygian_clear_time = max(
        to_int(stygian_clear_time),
        0,
    )

    theater_value = (
        10
        * theater_act
        * theater_stars
    )

    friendship_value = (
        friendship_count
        * FRIENDSHIP_MULTIPLIER
    )

    if stygian_clear_time > 0:
        stygian_time_value = max(
            360 - stygian_clear_time,
            0,
        )
    else:
        stygian_time_value = 0

    raw_stygian_point = calculate_stygian_point(
        stygian_difficulty,
        stygian_clear_time,
    )

    # 開催倍率は幽境ポイントだけに掛ける
    stygian_value = round(
        raw_stygian_point
        * get_stygian_multiplier()
    )

    base_value = (
        achievements
        + theater_value
        + friendship_value
        + stygian_time_value
        + stygian_value
    )

    # 36★なら1倍、35★以下なら0倍
    abyss_multiplier = max(
        abyss_stars - 35,
        0,
    )

    return round(
        base_value
        * abyss_multiplier
    )


# =====================================
# 理論プロフィール値
# =====================================

THEORETICAL_PROFILE_VALUE = calculate_profile_value(
    achievements=THEORY_ACHIEVEMENT,
    theater_act=THEORY_THEATER_ACT,
    theater_stars=THEORY_THEATER_STARS,
    friendship_count=THEORY_FRIENDSHIP_COUNT,
    abyss_stars=THEORY_ABYSS_STARS,
    stygian_difficulty=6,
    stygian_clear_time=THEORY_STYGIAN_CLEAR_TIME,
)


# =====================================
# 100点採点：アチーブメント
# 基本30点＋最大5点ボーナス
# =====================================

def score_achievement(achievements) -> int:
    achievements = max(to_int(achievements), 0)

    # 1752を超えた分は1個につき+1点
    # 1757で最大35点
    if achievements > ACHIEVEMENT_FULL_SCORE_COUNT:
        bonus = (
            achievements
            - ACHIEVEMENT_FULL_SCORE_COUNT
        )

        return min(
            30 + bonus,
            35,
        )

    rate = (
        achievements
        / ACHIEVEMENT_FULL_SCORE_COUNT
        * 100
    )

    if rate >= 100:
        return 30
    elif rate >= 99:
        return 29
    elif rate >= 98:
        return 28
    elif rate >= 97:
        return 27
    elif rate >= 96:
        return 26
    elif rate >= 95:
        return 25
    elif rate >= 90:
        return 23
    elif rate >= 85:
        return 20
    elif rate >= 80:
        return 17
    elif rate >= 70:
        return 13
    elif rate >= 60:
        return 9
    elif rate >= 50:
        return 6
    elif rate >= 40:
        return 3
    elif rate >= 30:
        return 2
    elif rate >= 20:
        return 1
    else:
        return 0


# =====================================
# 100点採点：幻想シアター
# 最大24点
# =====================================

def score_theater(
    theater_act,
    theater_stars,
) -> int:
    theater_act = max(to_int(theater_act), 0)
    theater_stars = max(to_int(theater_stars), 0)

    if theater_act <= 0:
        return 0

    # 星1つにつき2点
    return min(
        theater_stars * 2,
        24,
    )


# =====================================
# 100点採点：幽境の激戦
# 基本最大25点＋タイムボーナス最大5点
# =====================================

def score_stygian(
    difficulty,
    clear_time,
) -> int:
    difficulty = max(to_int(difficulty), 0)
    clear_time = max(to_int(clear_time), 0)

    # 基本点
    if difficulty >= 6:
        if 0 < clear_time <= 180:
            base_score = 25
        else:
            base_score = 20

    elif difficulty == 5:
        base_score = 15

    elif difficulty == 4:
        base_score = 10

    elif difficulty == 3:
        base_score = 5

    else:
        return 0

    time_bonus = 0

    # アルティメット・180秒以内のみ対象
    if difficulty >= 6 and 0 < clear_time <= 180:
        if clear_time <= 59:
            time_bonus = 5
        elif clear_time <= 69:
            time_bonus = 4
        elif clear_time <= 79:
            time_bonus = 3
        elif clear_time <= 89:
            time_bonus = 2
        elif clear_time <= 99:
            time_bonus = 1

    return base_score + time_bonus


# =====================================
# 100点採点：深境螺旋
# 最大15点
# =====================================

def score_abyss(abyss_stars) -> int:
    abyss_stars = max(to_int(abyss_stars), 0)

    if abyss_stars >= 36:
        return 15
    elif abyss_stars >= 33:
        return 13
    elif abyss_stars >= 30:
        return 10
    elif abyss_stars >= 27:
        return 7
    elif abyss_stars >= 18:
        return 3
    else:
        return 0


# =====================================
# 100点採点：好感度MAX
# 最大5点
# =====================================

def score_friendship(friendship_count) -> int:
    friendship_count = max(
        to_int(friendship_count),
        0,
    )

    if THEORY_FRIENDSHIP_COUNT <= 0:
        return 0

    score = (
        friendship_count
        / THEORY_FRIENDSHIP_COUNT
        * 5
    )

    return max(
        0,
        min(round(score), 5),
    )


# =====================================
# 100点採点：冒険ランク
# 最大1点
# =====================================

def score_ar(ar) -> int:
    ar = max(to_int(ar), 0)

    if ar >= 60:
        return 1

    return 0


# =====================================
# 総合スコア
# 基本100点＋ボーナス最大10点
# =====================================

def calculate_total_score(
    achievement_score,
    theater_score,
    stygian_score,
    abyss_score,
    friendship_score,
    ar_score,
) -> int:
    total = (
        to_int(achievement_score)
        + to_int(theater_score)
        + to_int(stygian_score)
        + to_int(abyss_score)
        + to_int(friendship_score)
        + to_int(ar_score)
    )

    return max(
        0,
        min(total, MAX_TOTAL_SCORE),
    )


# =====================================
# 総合ランク
# =====================================

def rank_name(total) -> str:
    total = to_int(total)

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
        