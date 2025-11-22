import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import json
import os

EVENT_FILE = "event.json"

def load_event_data():
    if not os.path.exists(EVENT_FILE):
        raise FileNotFoundError(f"{EVENT_FILE} not found!")
    with open(EVENT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="event",
        description="Check the current event and its details"
    )
    async def event(self, ctx):
        try:
            data = load_event_data()
        except Exception as e:
            return await ctx.send(f"⚠️ Failed to load event.json: {e}")

        event_name = data.get("event_name", "Unknown Event")
        event_emoji = data.get("event_emoji", "❓")
        event_purpose = data.get("event_purpose", "No information available.")

        orb_emoji = data.get("orb", {}).get("emoji", "❓")
        orb_name = data.get("orb", {}).get("name", "Unknown Orb")

        start_str = data.get("start", "2025-11-01 00:00:00")
        end_str = data.get("end", "2025-11-10 09:00:00")

        try:
            start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return await ctx.send("⚠️ Invalid date format in event.json. Use YYYY-MM-DD HH:MM:SS")

        chances = data.get("chances", {})
        coins_rate = chances.get("coins", 40)
        coll_rate = chances.get("collectible", 10)
        orb_rate = chances.get("orb", 1)

        commands_used = data.get("commands", {})
        cmd = commands_used.get("command")
        orbs_cmd = commands_used.get("orbs_command", "aorbs")

        collectibles = data.get("collectibles", [])
        collectibles_list = "\n".join([f"{item.get('emoji', '')} {item.get('name', '')}" for item in collectibles])

        embed = discord.Embed(
            title=f"{event_emoji} {event_name}",
            color=discord.Color.from_str("#ff6b6b")
        )

        embed.add_field(
            name="What is this month celebrating?",
            value=event_purpose,
            inline=False
        )

        embed.add_field(
            name=f"**Duration:** <t:{int(start_time.timestamp())}:D> to <t:{int(end_time.timestamp())}:f>",
            value="\u200b",
            inline=False
        )

        embed.add_field(
            name="Event Collectibles:",
            value=(
                f"- There are **{len(collectibles)} event collectibles**:\n"
                f"{collectibles_list if collectibles_list else 'No collectibles set.'}\n\n"
                f"- There is **1 Special Orb:** {orb_emoji} **{orb_name}**\n"
                f"- Chances:\n"
                f" • 1–10 Coins: **{coins_rate}%**\n"
                f" • Event Collectible: **{coll_rate}%**\n"
                f" • Orb: **{orb_rate}%**"
            ),
            inline=False
        )

        embed.add_field(
            name="Commands:",
            value=(
                f"Use the special event command: **`{cmd}`**\n"
                f"You can check the orbs you've gained using: **`{orbs_cmd}`**"
            ),
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Event(bot))
