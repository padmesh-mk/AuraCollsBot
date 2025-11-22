import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import os

CHANNEL_ID = 1400518914097676539
POINTS_FILE = "coins.json"

class PointsLeaderboardSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sent_today = False
        self.send_lb_daily.start() 

    def cog_unload(self):
        self.send_lb_daily.cancel()

    @tasks.loop(minutes=1)
    async def send_lb_daily(self):
        await self.bot.wait_until_ready() 
        now = datetime.utcnow() + timedelta(hours=5, minutes=30)

        if now.hour == 9 and now.minute == 0 and not self.sent_today:
            await self.send_leaderboard()
            self.sent_today = True
        elif now.hour != 9:
            self.sent_today = False

    async def send_leaderboard(self):
        channel = self.bot.get_channel(CHANNEL_ID)
        if not channel:
            print(f"[PointsLeaderboardSender] Channel with ID {CHANNEL_ID} not found.")
            return

        if not os.path.exists(POINTS_FILE):
            await channel.send("📛 No coins data available.")
            return

        with open(POINTS_FILE, "r") as f:
            data = json.load(f)

        if not data:
            await channel.send("📛 No coins data available.")
            return

        points_lb = sorted(data.items(), key=lambda x: x[1], reverse=True)

        embed = discord.Embed(
            title="<:ac_coins:1400522330668794028> Coins Leaderboard",
            color=0xFF6B6B
        )

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        lines = []

        for idx, (user_id, coins) in enumerate(points_lb[:10], start=1):
            emoji = emoji_map.get(idx, f"#{idx}")
            member = self.bot.get_user(int(user_id))
            username = member.name if member else f"`{user_id}`"
            lines.append(f"{emoji}  `{coins}` – {username}")


        embed.add_field(
            name="Top 10 Coin Holders",
            value="\n".join(lines),
            inline=False
        )

        ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        embed.set_footer(
            text=f"Last updated: {ist_now.strftime('%Y-%m-%d %I:%M %p IST')} • Next update in 24 hours"
        )

        await channel.send(embed=embed)

    @send_lb_daily.before_loop
    async def before_leaderboard(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(PointsLeaderboardSender(bot))
