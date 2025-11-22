import discord
from discord.ext import commands
import json
from datetime import datetime

OWNER_ID = 941902212303556618
LOG_FILE = "coll_logs.json"

class CollLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clog")
    async def clog(self, ctx):
        """Owner-only collectible log viewer"""
        if ctx.author.id != OWNER_ID:
            return await ctx.reply("<:ap_crossmark:1382760353904988230> You don't have permission to use this command.")

        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return await ctx.reply("No logs found or file is invalid.")

        if not logs:
            return await ctx.reply("No logs available.")

        logs = list(reversed(logs))

        pages = []
        for i in range(0, len(logs), 10):
            chunk = logs[i:i+10]
            desc = ""
            for log in chunk:
                time = datetime.fromtimestamp(log["timestamp"]).strftime("%d %b %Y %H:%M:%S")
                desc += f"**{time}** - `{log['from_name']}` sent `{log['to_name']}`: **{log['collectible']}**\n"
            embed = discord.Embed(
                title="📜 Collectible Log",
                description=desc,
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"Page {len(pages)+1}/{(len(logs)-1)//10 + 1}")
            pages.append(embed)

        current_page = 0
        msg = await ctx.send(embed=pages[current_page])

        await msg.add_reaction("<:ap_backward:1382775479202746378>")
        await msg.add_reaction("<:ap_forward:1382775383371419790>")

        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["<:ap_backward:1382775479202746378>", "<:ap_forward:1382775383371419790>"]
                and reaction.message.id == msg.id
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                await msg.remove_reaction(reaction, user)

                if str(reaction.emoji) == "<:ap_forward:1382775383371419790>" and current_page < len(pages) - 1:
                    current_page += 1
                    await msg.edit(embed=pages[current_page])
                elif str(reaction.emoji) == "<:ap_backward:1382775479202746378>" and current_page > 0:
                    current_page -= 1
                    await msg.edit(embed=pages[current_page])

            except TimeoutError:
                break
            except Exception:
                break

async def setup(bot):
    await bot.add_cog(CollLog(bot))
