# score.py

THEORY_ACHIEVEMENT = 1757


# ======================
# 冒険ランク（10点）
# ======================
def score_ar(ar: int) -> int:
    if ar >= 60:
        return 10
    elif ar == 59:
        return 9
    elif ar == 58:
        return 8
    elif ar == 57:
        return 7
    elif ar == 56:
        return 6
    elif ar == 55:
        return 5
    elif ar >= 50:
        return 4
    elif ar >= 45:
        return 3
    elif ar >= 40:
        return 2
    elif ar >= 30:
        return 1
    else:
        return 0


# ======================
# 深境螺旋（20点）
# ======================
def score_abyss(stars: int) -> int:
    if stars >= 36:
        return 20
    elif stars >= 33:
        return 18
    elif stars >= 30:
        return 15
    elif stars >= 27:
        return 10
    elif stars >= 18:
        return 5
    else:
        return 0


# ======================
# 幻想シアター（20点）
# ======================
def score_theater(act: int, stars: int) -> int:
    if act <= 0:
        return 0

    if act >= 10:
        if stars >= 12:
            return 20
        elif stars >= 10:
            return 18
        elif stars >= 8:
            return 15
        else:
            return 14

    if act == 9:
        return 14
    elif act == 8:
        return 12
    elif act == 7:
        return 10
    elif act == 6:
        return 8
    else:
        return 5


# ======================
# 幽境の激戦（20点）
# ======================
def score_stygian(difficulty, clear_time) -> int:
    try:
        difficulty = int(difficulty)
    except (TypeError, ValueError):
        return 0

    try:
        clear_time = int(clear_time)
    except (TypeError, ValueError):
        clear_time = 0

    if difficulty >= 6:
        if 0 < clear_time <= 180:
            return 20
        return 18

    elif difficulty == 5:
        return 15
    elif difficulty == 4:
        return 12
    elif difficulty == 3:
        return 8
    elif difficulty == 2:
        return 5
    elif difficulty == 1:
        return 2
    else:
        return 0


# ======================
# アチーブメント（30点）
# ======================
def score_achievement(achievement: int) -> int:
    if THEORY_ACHIEVEMENT <= 0:
        return 0

    rate = achievement / THEORY_ACHIEVEMENT * 100

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


# ======================
# 総合ランク
# ======================
def rank_name(total: int) -> str:
    if total >= 98:
        return "SSS"
    elif total >= 95:
        return "SS+"
    elif total >= 90:
        return "SS"
    elif total >= 85:
        return "S"
    elif total >= 80:
        return "A+"
    elif total >= 75:
        return "A"
    elif total >= 70:
        return "B+"
    elif total >= 60:
        return "B"
    elif total >= 50:
        return "C"
    else:
        return "D"