# bot.py

import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from app import (
    calculate_player_data,
    detect_server,
)


# =====================================
# 環境変数
# =====================================

load_dotenv()

DISCORD_TOKEN = os.environ.get(
    "DISCORD_TOKEN"
)

SITE_URL = os.environ.get(
    "SITE_URL",
    "https://genshin-checker.onrender.com/",
)


# =====================================
# Bot設定
# =====================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)


SERVER_LABELS = {
    "asia": "🌏 Asia",
    "america": "🇺🇸 America",
    "europe": "🇪🇺 Europe",
    "tw": "🇹🇼 TW / HK / MO",
    "cn": "🇨🇳 China",
    "unknown": "❓ Unknown",
}


# =====================================
# 起動処理
# =====================================

@bot.event
async def on_ready():
    try:
        synced_commands = await bot.tree.sync()

        print(
            f"スラッシュコマンドを"
            f"{len(synced_commands)}件同期しました。"
        )

    except Exception as error:
        print(
            "コマンド同期エラー："
            f"{type(error).__name__}: {error}"
        )

    print(
        "Bot起動成功："
        f"{bot.user}"
    )


# =====================================
# 動作確認
# =====================================

@bot.tree.command(
    name="ping",
    description="Botが動いているか確認します",
)
async def ping(
    interaction: discord.Interaction,
):
    await interaction.response.send_message(
        "🏓 Pong!",
        ephemeral=True,
    )


# =====================================
# UID採点
# =====================================

@bot.tree.command(
    name="score",
    description="原神プロフィールを採点します",
)
@app_commands.describe(
    uid="9桁または10桁の原神UID",
)
async def score_command(
    interaction: discord.Interaction,
    uid: str,
):
    uid_text = uid.strip()

    # UID入力チェック
    if not uid_text.isdigit():
        await interaction.response.send_message(
            "UIDは数字で入力してください。",
            ephemeral=True,
        )
        return

    if len(uid_text) not in (
        9,
        10,
    ):
        await interaction.response.send_message(
            "UIDは9桁または10桁で入力してください。",
            ephemeral=True,
        )
        return

    # Enka取得には時間がかかるため先に応答を保留
    await interaction.response.defer()

    uid_number = int(uid_text)

    try:
        # 同期処理を別スレッドで実行し、
        # Discord Bot全体が固まらないようにする
        player_data = await asyncio.to_thread(
            calculate_player_data,
            uid_number,
        )

        player = player_data["player"]

        nickname = (
            player.nickname
            or "Unknown Player"
        )

        total_score = player_data["total"]
        max_total_score = player_data[
            "max_total_score"
        ]
        rank_result = player_data["rank"]
        profile_value = player_data[
            "profile_value"
        ]
        icon_url = player_data["icon_url"]

        server_key = detect_server(
            uid_number
        )

        server_label = SERVER_LABELS.get(
            server_key,
            SERVER_LABELS["unknown"],
        )

        # =====================================
        # Discord Embed
        # =====================================

        embed = discord.Embed(
            title=f"🎮 {nickname}",
            description=(
                f"UID：`{uid_text}`"
            ),
            url=(
                f"{SITE_URL.rstrip('/')}"
                f"/rank?uid={uid_text}"
            ),
        )

        embed.add_field(
            name="⭐ 総合スコア",
            value=(
                f"**{total_score}"
                f" / {max_total_score}**"
            ),
            inline=True,
        )

        embed.add_field(
            name="🏆 ランク",
            value=f"**{rank_result}**",
            inline=True,
        )

        embed.add_field(
            name="💎 プロフィール値",
            value=(
                f"**{profile_value:,}**"
            ),
            inline=True,
        )

        embed.add_field(
            name="🌍 サーバー",
            value=server_label,
            inline=False,
        )

        if icon_url:
            embed.set_thumbnail(
                url=icon_url
            )

        embed.set_footer(
            text="原神プロフィール格付け"
        )

        await interaction.followup.send(
            embed=embed
        )

    except Exception as error:
        print(
            "Discord UID採点エラー："
            f"{type(error).__name__}: {error}"
        )

        await interaction.followup.send(
            (
                "プロフィールを取得できませんでした。\n"
                "UID、ゲーム内プロフィールの公開設定、"
                "Enka.Networkの状態を確認してください。"
            ),
            ephemeral=True,
        )


# =====================================
# Bot起動
# =====================================

if not DISCORD_TOKEN:
    raise RuntimeError(
        "DISCORD_TOKENが.envに設定されていません。"
    )


bot.run(
    DISCORD_TOKEN
)