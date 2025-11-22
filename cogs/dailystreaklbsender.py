import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import os

CHANNEL_ID = 1400518876030304399
DAILY_FILE = "daily.json"

class DailyStreakLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sent_today = False
        self.send_streak_lb.start()

    def cog_unload(self):
        self.send_streak_lb.cancel()

    @tasks.loop(minutes=1)
    async def send_streak_lb(self):
        now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        if now.hour == 9 and now.minute == 0 and not self.sent_today:
            await self.send_leaderboard()
            self.sent_today = True
        elif now.minute != 0:
            self.sent_today = False

    async def send_leaderboard(self):
        channel = self.bot.get_channel(CHANNEL_ID)
        if not channel:
            print(f"[StreakLeaderboard] Channel with ID {CHANNEL_ID} not found.")
            return

        if not os.path.exists(DAILY_FILE):
            await channel.send("📛 No streak data available.")
            return

        with open(DAILY_FILE, "r") as f:
            data = json.load(f)

        streak_lb = sorted(data.items(), key=lambda x: x[1].get("streak", 0), reverse=True)
        if not streak_lb:
            await channel.send("📛 No streak data available.")
            return

        embed = discord.Embed(
            title="<:ap_chart:1384942967642394654> Daily Streak Leaderboard",
            color=0xFF6B6B
        )

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        lines = []

        for idx, (user_id, info) in enumerate(streak_lb[:10], start=1):
            emoji = emoji_map.get(idx, f"#{idx}")
            streak = info.get("streak", 0)
            member = self.bot.get_user(int(user_id))
            username = member.name if member else f"`{user_id}`"
            mention = member.mention if member else f"<@{user_id}>"
            lines.append(f"{emoji}  `{streak}` – {username}")

        embed.add_field(name="Top 10 Streaks", value="\n".join(lines), inline=False)

        ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        embed.set_footer(text=f"Last updated: {ist_now.strftime('%Y-%m-%d %I:%M %p IST')} • Next update in 24 hours")

        await channel.send(embed=embed)

    @send_streak_lb.before_loop
    async def before_leaderboard(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(DailyStreakLeaderboard(bot))