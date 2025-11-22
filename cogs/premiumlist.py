import discord
from discord.ext import commands
import json
from datetime import datetime

PREMIUM_FILE = "premium.json"

OWNER_ID = 941902212303556618 

class PremiumView(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_premium(self):
        try:
            with open(PREMIUM_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"users": {}}

    @commands.hybrid_command(name="premiumlist", description="Show all premium members with details")
    async def premiumlist(self, ctx):
        if ctx.author.id != OWNER_ID:
            await ctx.send("<:ac_crossmark:1399650396322005002> You are not allowed to use this command.", ephemeral=True if ctx.interaction else False)
            return

        data = self.load_premium()
        users = data.get("users", {})

        if not users:
            await ctx.send("<:ac_ducksad:1409944288522928199> No premium members found.")
            return

        embed = discord.Embed(
            title="<:ac_premium:1412065919882235914> Premium Members",
            color=discord.Color.from_str("#ff6b6b")
        )

        for user_id, details in users.items():
            user = self.bot.get_user(int(user_id))
            name = user.name if user else "Unknown User"
            start_time = details.get("start", "N/A")
            expiry_time = details.get("expiry", "N/A")

            try:
                if start_time != "N/A":
                    start_ts = datetime.fromisoformat(start_time)
                    start_fmt = f"<t:{int(start_ts.timestamp())}:F> (<t:{int(start_ts.timestamp())}:R>)"
                else:
                    start_fmt = "N/A"

                if expiry_time != "N/A":
                    expiry_ts = datetime.fromisoformat(expiry_time)
                    expiry_fmt = f"<t:{int(expiry_ts.timestamp())}:F> (<t:{int(expiry_ts.timestamp())}:R>)"
                else:
                    expiry_fmt = "N/A"
            except:
                start_fmt = start_time
                expiry_fmt = expiry_time

            embed.add_field(
                name=f"{name} ({user_id})",
                value=f"**From:** {start_fmt}\n**Expiry:** {expiry_fmt}",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PremiumView(bot))
