import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio

COLLECTIBLES_FILE = "collectibles.json"
LOG_CHANNEL_ID = 1407684759123132537
OWNER_ID = 941902212303556618

_file_lock = asyncio.Lock()

async def ensure_file_exists():
    if not os.path.exists(COLLECTIBLES_FILE):
        with open(COLLECTIBLES_FILE, "w") as f:
            json.dump({}, f)

async def load_collectibles():
    await ensure_file_exists()
    async with _file_lock:
        with open(COLLECTIBLES_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

async def save_collectibles(data):
    async with _file_lock:
        tmp_path = COLLECTIBLES_FILE + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=4)
        os.replace(tmp_path, COLLECTIBLES_FILE)


async def update_collectible(user_id: int, collectible: str, amount: int):
    """Safely modify a user's collectible count with cross-cog persistence."""
    user_id = str(user_id)
    async with _file_lock:
        if not os.path.exists(COLLECTIBLES_FILE):
            data = {}
        else:
            with open(COLLECTIBLES_FILE, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}

        if user_id not in data:
            data[user_id] = {}

        new_value = max(0, data[user_id].get(collectible, 0) + amount)
        data[user_id][collectible] = new_value

        tmp_path = COLLECTIBLES_FILE + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=4)
        os.replace(tmp_path, COLLECTIBLES_FILE)

    return new_value


class CollAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="colladmin",
        description="Give or take collectibles from a user (Owner only)."
    )
    @app_commands.describe(
        action="Choose give or take",
        member="The target user",
        collectible="The collectible name",
        amount="How many to give or take"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Give", value="give"),
            app_commands.Choice(name="Take", value="take")
        ]
    )
    async def colladmin(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        member: discord.Member,
        collectible: str,
        amount: int
    ):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "<:ap_crossmark:1382760353904988230> Only the bot owner can use this command.",
                ephemeral=True
            )
            return

        if action.value == "give":
            new_count = await update_collectible(member.id, collectible, amount)
            msg = f"<:ap_checkmark:1382760062728273920> Added {amount}x **{collectible}** to {member.mention} (Now: {new_count})"
        elif action.value == "take":
            new_count = await update_collectible(member.id, collectible, -amount)
            msg = f"<:ap_checkmark:1382760062728273920> Removed {amount}x **{collectible}** from {member.mention} (Now: {new_count})"
        else:
            await interaction.response.send_message(
                "<:ap_crossmark:1382760353904988230> Invalid action.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(msg)

        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="📦 Collectible Admin Action",
                color=discord.Color.orange()
            )
            embed.add_field(name="Action", value=action.name, inline=True)
            embed.add_field(name="User", value=f"{member} (`{member.id}`)", inline=True)
            embed.add_field(name="Collectible", value=collectible, inline=True)
            embed.add_field(name="Amount", value=str(amount), inline=True)
            embed.add_field(name="Invoker", value=f"{interaction.user} (`{interaction.user.id}`)", inline=False)

            if interaction.response.is_done():
                message_id = (await interaction.original_response()).id
            else:
                message_id = interaction.id
            message_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{message_id}"
            embed.add_field(name="Message Link", value=f"[Jump to Message]({message_link})", inline=False)

            await log_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CollAdmin(bot))
