import discord
from discord.ext import commands
import json, os, random
from datetime import datetime, timedelta

WEEKLY_FILE = "weekly.json"
COINS_FILE = "coins.json"
COLLECTIBLES_FILE = "collectibles.json"
INFO_FILE = "collectible_info.json"
PREMIUM_FILE = "premium.json"

WEEKLY_COLLECTIBLES = ["red puffle", "cyan puffle", "white puffle", "discord puffle"]

def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def is_premium(user_id: int):
    data = load_json(PREMIUM_FILE).get("users", {})
    user_info = data.get(str(user_id))
    if not user_info:
        return False
    expiry = datetime.fromisoformat(user_info["expiry"])
    return datetime.utcnow() < expiry

class Weekly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def add_coins(self, user_id: str, amount: int):
        coins = load_json(COINS_FILE)
        coins[str(user_id)] = coins.get(str(user_id), 0) + amount
        save_json(COINS_FILE, coins)

    def add_collectible(self, user_id: str, item: str):
        collectibles = load_json(COLLECTIBLES_FILE)
        if str(user_id) not in collectibles:
            collectibles[str(user_id)] = {}
        collectibles[str(user_id)][item] = collectibles[str(user_id)].get(item, 0) + 1
        save_json(COLLECTIBLES_FILE, collectibles)

    async def claim_weekly(self, ctx_or_interaction, user):
        weekly_data = load_json(WEEKLY_FILE)
        user_id = str(user.id)

        now = datetime.utcnow()
        cooldown = timedelta(days=7)

        if user_id not in weekly_data:
            weekly_data[user_id] = {"last_claim": None, "streak": 0}

        last_claim_iso = weekly_data[user_id]["last_claim"]
        streak = weekly_data[user_id]["streak"]

        if last_claim_iso:
            last_claim = datetime.fromisoformat(last_claim_iso)
            if now < last_claim + cooldown:
                remaining = (last_claim + cooldown) - now
                remaining_text = f"{remaining.days}d {remaining.seconds//3600}h {(remaining.seconds//60)%60}m"
                embed = discord.Embed(
                    description=f"<:ap_time:1382729675616555029> {user.display_name}, you already claimed your weekly!",
                    color=discord.Color.red(),
                )
                embed.set_footer(text=f"Come back in {remaining_text}")
                
                if isinstance(ctx_or_interaction, commands.Context):
                    return await ctx_or_interaction.reply(embed=embed)
                else:
                    return await ctx_or_interaction.response.send_message(embed=embed)

        points = 100

        bonus = 100 if is_premium(user.id) else 0
        total_points = points + bonus
        self.add_coins(user_id, total_points)

        collectible_info = load_json(INFO_FILE)

        chosen = random.choice(WEEKLY_COLLECTIBLES)
        self.add_collectible(user_id, chosen)

        coll_emoji = collectible_info.get(chosen, {}).get("emoji", "")

        weekly_data[user_id]["last_claim"] = now.isoformat()
        weekly_data[user_id]["streak"] = streak + 1
        save_json(WEEKLY_FILE, weekly_data)

        embed = discord.Embed(
            description=(
                f"<:ac_coins:1400522330668794028> **{user.display_name}**, Here is your weekly **{points} Coins**"
                + (f" + **{bonus} Premium Bonus Coins**" if bonus else "")
                + f"!\n\n"
                f"<:ac_blank:1399434326591934515> You're on a **{weekly_data[user_id]['streak']} weekly streak**!\n"
                f"{coll_emoji} You received a **{chosen}**!"
            ),
            color=discord.Color.from_str("#ff6b6b"),
        )
        embed.set_footer(text=f"Your next weekly is available in: 7d")

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.reply(embed=embed)
        else:
            await ctx_or_interaction.response.send_message(embed=embed)

    @commands.hybrid_command(name="weekly", description="Claim your weekly rewards")
    async def weekly_slash(self, ctx):
        await self.claim_weekly(ctx, ctx.author)

async def setup(bot):
    await bot.add_cog(Weekly(bot))
