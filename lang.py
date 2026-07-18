# lang.py

SUPPORTED_LANGUAGES = {
    "ja",
    "en",
    "zh",
}


TEXTS = {
    "ja": {
        # =====================================
        # 共通
        # =====================================
        "html_lang": "ja",
        "site_title": "原神プロフィール格付け",
        "eyebrow": "GENSHIN PROFILE RANK",
        "language_label": "言語",
        "criteria_button": "採点基準を見る",
        "ranking_button": "ランキングを見る",
        "score_button": "採点する",
        "people_unit": "人",
        "created_by": "製作者",
        "scoring_formula_by": "計算式提供",
        "powered_by": "Powered by",
        "unofficial_notice": "※ 本サイトは非公式のファンサイトです。",

        # =====================================
        # トップページ
        # =====================================
        "home_description": (
            "UIDを入力すると、Enka.Networkの公開プロフィールをもとに、"
            "110点満点で自動採点します。"
        ),
        "uid_label": "原神UID",
        "uid_placeholder": "例：800123456 または 1800123456",
        "ranking_count_label": "現在のランキング登録者数：",
        "notice": (
            "ゲーム内プロフィールで戦績を公開してから採点してください。"
        ),

        # =====================================
        # 入力・取得エラー
        # =====================================
        "uid_numeric_error": "UIDは数字で入力してください。",
        "uid_length_error": "UIDは9桁または10桁で入力してください。",
        "profile_fetch_error": (
            "プロフィールを取得できませんでした。"
            "UID、ゲーム内プロフィールの公開設定、"
            "Enka.Networkの状態を確認してください。"
        ),
        "ranking_invalid_uid_error": (
            "ランキング登録用UIDが正しくありません。"
        ),
        "ranking_profile_zero_error": (
            "プロフィール値が0のため、ランキングへ登録できません。"
        ),
        "ranking_registration_error": (
            "ランキング登録に失敗しました。"
            "時間を置いて再度お試しください。"
        ),

        # =====================================
        # 結果画面
        # =====================================
        "result_overall_rank": "総合ランク",
        "result_score_summary": "基本100点＋ボーナス最大10点",
        "result_profile_value": "プロフィール値",
        "result_theoretical_value": "理論値",
        "result_achievements": "アチーブメント",
        "result_achievement_detail_1": "1752個で基本30点",
        "result_achievement_detail_2": (
            "1753～1757個は最大＋5点"
        ),
        "result_profile_value_addition": "プロフィール値への加算",
        "result_theater": "幻想シアター",
        "result_act_prefix": "第",
        "result_act_suffix": "幕",
        "result_theater_detail": "★1につき2点",
        "result_stygian": "幽境の激戦",
        "result_difficulty": "難易度",
        "result_seconds": "秒",
        "result_not_challenged": "未挑戦",
        "result_stygian_detail": (
            "基本最大25点／99秒以下からタイムボーナス／"
            "59秒以下で＋5点"
        ),
        "result_time_bonus": "タイム加算",
        "result_stygian_point": "幽境ポイント",
        "result_total_addition": "幽境による合計加算：",
        "result_abyss": "深境螺旋",
        "result_abyss_multiplier": "プロフィール値の螺旋倍率：",
        "result_friendship": "好感度MAXキャラ",
        "result_character": "人につき",
        "result_ar": "冒険ランク",
        "result_ar_detail": "AR60で1点",
        "result_registered": "ランキングに登録しました！",
        "result_current_rank": "現在の順位は",
        "result_rank_suffix": "位です。",
        "result_update_notice": (
            "同じUIDで再登録すると、"
            "最新のプロフィール情報へ更新されます。"
        ),
        "result_register_question": "ランキングに登録しますか？",
        "result_register_description": (
            "登録すると、ニックネーム・プロフィール画像・"
            "プロフィール値・総合スコア・ランクが公開されます。"
        ),
        "result_update": "最新プロフィールで更新する",
        "result_register": "はい、登録する",
        "result_cancel": "いいえ、登録しない",
        "result_profile_zero": (
            "プロフィール値が0のため、"
            "現在はランキングへ登録できません。"
        ),
        "result_save_image": "結果画像を保存",
        "result_another_uid": "別のUIDを採点する",

        # =====================================
        # 採点基準ページ
        # =====================================
        "criteria_page_title": "採点基準",
        "criteria_description": (
            "各項目の採点方法とプロフィール値の計算式を表示します。"
        ),
        "criteria_total_score": "総合スコア",
        "criteria_profile_value": "プロフィール値",
        "criteria_back_home": "トップへ戻る",
        "criteria_view_ranking": "ランキングを見る",

        # =====================================
        # ランキングページ
        # =====================================
        "ranking_page_title": "プロフィール値ランキング",
        "ranking_description": (
            "当サイトで登録された公開プロフィールを、"
            "プロフィール値の高い順に表示しています。"
        ),
        "ranking_count_text": "現在の登録人数：",
        "ranking_showing": "表示中：",
        "ranking_profile_value": "プロフィール値",
        "ranking_total_score": "総合スコア",
        "ranking_rank": "ランク",
        "ranking_updated": "更新",
        "ranking_empty_title": "まだランキング登録者がいません",
        "ranking_empty_description": (
            "UIDを採点して、"
            "最初のランキング登録者になってください。"
        ),
        "ranking_score_uid": "UIDを採点する",
    },

    "en": {
        # =====================================
        # Common
        # =====================================
        "html_lang": "en",
        "site_title": "Genshin Profile Ranking",
        "eyebrow": "GENSHIN PROFILE RANK",
        "language_label": "Language",
        "criteria_button": "Scoring Criteria",
        "ranking_button": "View Ranking",
        "score_button": "Calculate Score",
        "people_unit": "",
        "created_by": "Created by",
        "scoring_formula_by": "Scoring formula by",
        "powered_by": "Powered by",
        "unofficial_notice": "This is an unofficial fan-made website.",

        # =====================================
        # Home page
        # =====================================
        "home_description": (
            "Enter a UID to automatically score a public Enka.Network "
            "profile out of 110 points."
        ),
        "uid_label": "Genshin UID",
        "uid_placeholder": "Example: 800123456 or 1800123456",
        "ranking_count_label": "Registered ranking players:",
        "notice": (
            "Please make your battle records public in your in-game "
            "profile before calculating your score."
        ),

        # =====================================
        # Input and retrieval errors
        # =====================================
        "uid_numeric_error": "Please enter a numeric UID.",
        "uid_length_error": "The UID must contain 9 or 10 digits.",
        "profile_fetch_error": (
            "The profile could not be retrieved. Please check the UID, "
            "your in-game profile visibility settings, and the status "
            "of Enka.Network."
        ),
        "ranking_invalid_uid_error": (
            "The UID used for ranking registration is invalid."
        ),
        "ranking_profile_zero_error": (
            "This profile cannot be registered because its profile "
            "value is 0."
        ),
        "ranking_registration_error": (
            "Ranking registration failed. Please try again later."
        ),

        # =====================================
        # Result page
        # =====================================
        "result_overall_rank": "Overall Rank",
        "result_score_summary": (
            "100 base points + up to 10 bonus points"
        ),
        "result_profile_value": "Profile Value",
        "result_theoretical_value": "Theoretical Maximum",
        "result_achievements": "Achievements",
        "result_achievement_detail_1": (
            "30 base points at 1,752 achievements"
        ),
        "result_achievement_detail_2": (
            "Up to +5 points from 1,753 to 1,757"
        ),
        "result_profile_value_addition": "Profile value addition",
        "result_theater": "Imaginarium Theater",
        "result_act_prefix": "Act",
        "result_act_suffix": "",
        "result_theater_detail": "2 points per star",
        "result_stygian": "Stygian Onslaught",
        "result_difficulty": "Difficulty",
        "result_seconds": "sec",
        "result_not_challenged": "Not attempted",
        "result_stygian_detail": (
            "Up to 25 base points / time bonus from 99 seconds or less / "
            "+5 points at 59 seconds or less"
        ),
        "result_time_bonus": "Time addition",
        "result_stygian_point": "Stygian points",
        "result_total_addition": "Total Stygian addition:",
        "result_abyss": "Spiral Abyss",
        "result_abyss_multiplier": (
            "Spiral Abyss profile-value multiplier:"
        ),
        "result_friendship": "Max Friendship Characters",
        "result_character": "per character",
        "result_ar": "Adventure Rank",
        "result_ar_detail": "1 point at AR60",
        "result_registered": "Registered in the ranking!",
        "result_current_rank": "Your current position is",
        "result_rank_suffix": ".",
        "result_update_notice": (
            "Registering the same UID again will update it with the "
            "latest profile information."
        ),
        "result_register_question": (
            "Would you like to join the ranking?"
        ),
        "result_register_description": (
            "Your nickname, profile image, profile value, total score, "
            "and rank will be made public."
        ),
        "result_update": "Update with Latest Profile",
        "result_register": "Yes, Register",
        "result_cancel": "No, Do Not Register",
        "result_profile_zero": (
            "This profile cannot currently be registered because its "
            "profile value is 0."
        ),
        "result_save_image": "Save Result Image",
        "result_another_uid": "Score Another UID",

        # =====================================
        # Criteria page
        # =====================================
        "criteria_page_title": "Scoring Criteria",
        "criteria_description": (
            "View the scoring method for each category and the profile "
            "value formula."
        ),
        "criteria_total_score": "Total Score",
        "criteria_profile_value": "Profile Value",
        "criteria_back_home": "Back to Home",
        "criteria_view_ranking": "View Ranking",

        # =====================================
        # Ranking page
        # =====================================
        "ranking_page_title": "Profile Value Ranking",
        "ranking_description": (
            "Public profiles registered on this site are listed in "
            "descending order of profile value."
        ),
        "ranking_count_text": "Registered players:",
        "ranking_showing": "Showing:",
        "ranking_profile_value": "Profile Value",
        "ranking_total_score": "Total Score",
        "ranking_rank": "Rank",
        "ranking_updated": "Updated",
        "ranking_empty_title": "No players are registered yet",
        "ranking_empty_description": (
            "Score a UID and become the first player in the ranking."
        ),
        "ranking_score_uid": "Score a UID",
    },

    "zh": {
        # =====================================
        # 通用
        # =====================================
        "html_lang": "zh-CN",
        "site_title": "原神个人资料评分",
        "eyebrow": "GENSHIN PROFILE RANK",
        "language_label": "语言",
        "criteria_button": "查看评分标准",
        "ranking_button": "查看排行榜",
        "score_button": "开始评分",
        "people_unit": "人",
        "created_by": "网站制作",
        "scoring_formula_by": "评分公式提供",
        "powered_by": "数据支持",
        "unofficial_notice": "※ 本网站为非官方粉丝网站。",

        # =====================================
        # 首页
        # =====================================
        "home_description": (
            "输入UID后，系统将根据Enka.Network公开的个人资料，"
            "自动进行110分制评分。"
        ),
        "uid_label": "原神UID",
        "uid_placeholder": "示例：800123456 或 1800123456",
        "ranking_count_label": "当前排行榜注册人数：",
        "notice": "评分前，请先在游戏内个人资料中公开战绩。",

        # =====================================
        # 输入与获取错误
        # =====================================
        "uid_numeric_error": "UID只能输入数字。",
        "uid_length_error": "UID必须为9位或10位数字。",
        "profile_fetch_error": (
            "无法获取个人资料。请确认UID、游戏内个人资料公开设置，"
            "以及Enka.Network的运行状态。"
        ),
        "ranking_invalid_uid_error": "排行榜注册用UID不正确。",
        "ranking_profile_zero_error": (
            "个人资料值为0，无法注册到排行榜。"
        ),
        "ranking_registration_error": (
            "排行榜注册失败，请稍后重试。"
        ),

        # =====================================
        # 结果页面
        # =====================================
        "result_overall_rank": "综合等级",
        "result_score_summary": "基础100分＋最高10分奖励",
        "result_profile_value": "个人资料值",
        "result_theoretical_value": "理论值",
        "result_achievements": "成就",
        "result_achievement_detail_1": "1752个成就获得基础30分",
        "result_achievement_detail_2": (
            "1753～1757个成就最高追加5分"
        ),
        "result_profile_value_addition": "个人资料值加成",
        "result_theater": "幻想真境剧诗",
        "result_act_prefix": "第",
        "result_act_suffix": "幕",
        "result_theater_detail": "每颗星2分",
        "result_stygian": "幽境危战",
        "result_difficulty": "难度",
        "result_seconds": "秒",
        "result_not_challenged": "未挑战",
        "result_stygian_detail": (
            "基础最高25分／99秒以内开始获得时间奖励／"
            "59秒以内追加5分"
        ),
        "result_time_bonus": "时间加成",
        "result_stygian_point": "幽境点数",
        "result_total_addition": "幽境总加成：",
        "result_abyss": "深境螺旋",
        "result_abyss_multiplier": "深境螺旋个人资料值倍率：",
        "result_friendship": "满好感角色",
        "result_character": "每名角色",
        "result_ar": "冒险等阶",
        "result_ar_detail": "AR60获得1分",
        "result_registered": "已注册到排行榜！",
        "result_current_rank": "当前排名为",
        "result_rank_suffix": "名。",
        "result_update_notice": (
            "使用同一UID再次注册时，将更新为最新的个人资料信息。"
        ),
        "result_register_question": "是否注册到排行榜？",
        "result_register_description": (
            "注册后，昵称、头像、个人资料值、综合分数和等级将公开显示。"
        ),
        "result_update": "使用最新资料更新",
        "result_register": "是，注册",
        "result_cancel": "否，不注册",
        "result_profile_zero": (
            "个人资料值为0，目前无法注册到排行榜。"
        ),
        "result_save_image": "保存结果图片",
        "result_another_uid": "评分其他UID",

        # =====================================
        # 评分标准页面
        # =====================================
        "criteria_page_title": "评分标准",
        "criteria_description": (
            "查看各项目的评分方式及个人资料值计算公式。"
        ),
        "criteria_total_score": "综合分数",
        "criteria_profile_value": "个人资料值",
        "criteria_back_home": "返回首页",
        "criteria_view_ranking": "查看排行榜",

        # =====================================
        # 排行榜页面
        # =====================================
        "ranking_page_title": "个人资料值排行榜",
        "ranking_description": (
            "本网站已注册的公开个人资料将按照个人资料值从高到低显示。"
        ),
        "ranking_count_text": "当前注册人数：",
        "ranking_showing": "当前显示：",
        "ranking_profile_value": "个人资料值",
        "ranking_total_score": "综合分数",
        "ranking_rank": "等级",
        "ranking_updated": "更新日期",
        "ranking_empty_title": "目前还没有排行榜玩家",
        "ranking_empty_description": (
            "请先评分UID，成为第一位排行榜玩家。"
        ),
        "ranking_score_uid": "评分UID",
    },
}


def get_texts(language):
    """
    指定された言語の翻訳データを返す。
    未対応の言語なら日本語を返す。
    """

    language = str(
        language or "ja"
    ).strip().lower()

    if language not in SUPPORTED_LANGUAGES:
        language = "ja"

    return TEXTS[language]