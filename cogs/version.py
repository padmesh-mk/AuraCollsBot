# cogs/version.py
import discord
from discord.ext import commands
from discord import app_commands
import json
import os

VERSION_FILE = "version.json"

class Version(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.version_info = self.load_version()

    def load_version(self):
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r") as f:
                return json.load(f)
        return {
            "version": "Unknown",
            "last_updated": "Unknown",
            "developer": "Unknown",
            "changelog": []
        }

    @app_commands.command(name="version", description="Show the current bot version and recent updates")
    async def version(self, interaction: discord.Interaction):
        data = self.version_info
        embed = discord.Embed(
            title=f"<:ap_support:1382716862256910437> AuraColls v{data['version']}",
            color=0xFF6B6B,
            description=f"Created by **{data['developer']}**\nLast updated: `{data['last_updated']}`"
        )

        if data.get("changelog"):
            changelog = data["changelog"]
            for i in range(0, len(changelog), 5):
            	embed.add_field(
<<<<<<< HEAD
                	name="Recent Changes" if i == 0 else " ",
=======
                	name="Recent Changes" if i == 0 else "Continued",
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
                	value="\n".join(changelog[i:i + 5]),
                	inline=False
            )

<<<<<<< HEAD
        embed.set_footer(text="Upgrade to Premium to support the bot.")
=======
        embed.set_footer(text="Thank you for using AuraColls")
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Version(bot))
