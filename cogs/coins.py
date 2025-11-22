import discord
from discord.ext import commands
import json
import os

POINTS_FILE = "coins.json"
POINTS_EMOJI = "<:ac_coins:1400522330668794028>" 

def get_points(user_id):
    if not os.path.exists(POINTS_FILE):
        return 0

    with open(POINTS_FILE, "r") as f:
        data = json.load(f)

    return data.get(str(user_id), 0)

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="coins",
        description="Check your coins balance",
        aliases=["coin", "balance", "money", "bal"]
    )
    async def points(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        points = get_points(user.id)

        formatted_points = f"{points:,}"

        if user.id == ctx.author.id:
            msg = f"{POINTS_EMOJI} You’ve got **{formatted_points} coins** in your wallet!"
        else:
            msg = f"{POINTS_EMOJI} **{user.display_name}** has **{formatted_points} coins** in their wallet!"

        await ctx.reply(msg)

async def setup(bot):
    await bot.add_cog(Points(bot))
