import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import math

TRADABLE_FILE = "tradablecoll.json"
RESTRICTED_FILE = "restrictedcoll.json"
ALLOWED_USER_ID = 941902212303556618 
FIELDS_PER_PAGE = 25 

class CollDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_json(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def is_allowed_user(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == ALLOWED_USER_ID

    async def paginate_embed(self, interaction, title, color, fields_list):
        """Sends one or more embeds paginated if fields > 25."""
        if not fields_list:
            embed = discord.Embed(title=title, description="No collectibles found.", color=color)
            await interaction.response.send_message(embed=embed)
            return

        pages = math.ceil(len(fields_list) / FIELDS_PER_PAGE)
        for i in range(pages):
            embed = discord.Embed(title=f"{title} (Page {i+1}/{pages})", color=color)
            chunk = fields_list[i*FIELDS_PER_PAGE:(i+1)*FIELDS_PER_PAGE]
            for name, value, inline in chunk:
                embed.add_field(name=name, value=value, inline=inline)
            if i == 0:
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.followup.send(embed=embed)

    @app_commands.command(name="tradablecoll", description="View all tradable collectibles")
    async def tradablecoll(self, interaction: discord.Interaction):
        if not self.is_allowed_user(interaction):
            return await interaction.response.send_message(
                "<:ap_crossmark:1382760353904988230> You are not allowed to use this command.",
                ephemeral=True
            )

        data = self.load_json(TRADABLE_FILE)
        fields_list = []

        for key, item in data.items():
            emoji = item.get("emoji", "❓")
            name = item.get("name", key)
            fields_list.append((name, emoji, True)) 

        await self.paginate_embed(interaction, "📦 Tradable Collectibles", 0x90ee90, fields_list)

    @app_commands.command(name="ownercoll", description="View all restricted (owner-only) collectibles")
    async def ownercoll(self, interaction: discord.Interaction):
        if not self.is_allowed_user(interaction):
            return await interaction.response.send_message(
                "<:ap_crossmark:1382760353904988230> You are not allowed to use this command.",
                ephemeral=True
            )

        data = self.load_json(RESTRICTED_FILE)
        fields_list = []

        for key, item in data.items():
            emoji = item.get("emoji", "❓")
            name = item.get("name", key)
            owner_id = item.get("owner_id", 0)
            user = self.bot.get_user(owner_id)
            username = user.name if user else "Unknown User"
            mention = f"<@{owner_id}> ({username})"
            fields_list.append((name, f"{emoji} • {mention}", False)) 

        await self.paginate_embed(interaction, "🔒 Owner-Only Collectibles", 0xffcccb, fields_list)

async def setup(bot):
    await bot.add_cog(CollDisplay(bot))
