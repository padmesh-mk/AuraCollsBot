import discord
from discord.ext import commands, tasks
import asyncio
import random
import json
import os
import time
from datetime import datetime

COINS_FILE = "coins.json"
PREMIUM_FILE = "premium.json"
REMINDERS_FILE = "reminders.json"

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
    premium_data = load_json(PREMIUM_FILE)
    user_info = premium_data.get("users", {}).get(str(user_id))
    if not user_info:
        return False
    expiry = datetime.fromisoformat(user_info["expiry"])
    return datetime.utcnow() < expiry

def coinflip_cooldown(ctx: commands.Context):
    if is_premium(ctx.author.id):
        return commands.Cooldown(1, 3) 
    return commands.Cooldown(1, 15)   

class Coinflip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = {}
        self.reminder_loop.start()

    @commands.command(name="coinflip", aliases=["cf"])
    @commands.dynamic_cooldown(coinflip_cooldown, type=commands.BucketType.user)
    async def coinflip(self, ctx, amount: int = 1, choice: str = "heads"):
        coins = load_json(COINS_FILE)
        user_id = str(ctx.author.id)

        if user_id not in coins:
            coins[user_id] = 0

        if amount <= 0:
            return await ctx.send(f"<:ac_crossmark:1399650396322005002> **|** {ctx.author.mention} Invalid bet amount.")

        if coins[user_id] < amount:
            return await ctx.send(f"<:ac_crossmark:1399650396322005002> **|** {ctx.author.mention} You don’t have enough coins!")

        choice = choice.lower()
        if choice in ["head", "heads", "h"]:
            user_choice = "heads"
        elif choice in ["tail", "tails", "t"]:
            user_choice = "tails"
        else:
            user_choice = "heads"

        coins[user_id] -= amount
        save_json(COINS_FILE, coins)

        message = await ctx.send(
            f"**{ctx.author.display_name}** bet <:ac_coins:1400522330668794028> **{amount}** on **{user_choice}**\n"
            "*The coin spins.*"
        )

        for dots in [".", "..", "..."]:
            await asyncio.sleep(1)
            await message.edit(
                content=f"**{ctx.author.display_name}** bet <:ac_coins:1400522330668794028> **{amount}** on **{user_choice}**\n"
                        f"*The coin spins{dots}*"
            )

        result = random.choice(["heads", "tails"])
        result_emoji = "Head" if result == "heads" else "Tail"

        if result == user_choice:
            winnings = amount * 2
            coins[user_id] += winnings
            save_json(COINS_FILE, coins)
            await message.edit(
                content=f"**{ctx.author.display_name}** bet <:ac_coins:1400522330668794028> **{amount}** on **{user_choice}**\n"
                        f"The coin spins... **{result_emoji}** and you won **{winnings} coins**!!"
            )
        else:
            save_json(COINS_FILE, coins)
            await message.edit(
                content=f"**{ctx.author.display_name}** bet <:ac_coins:1400522330668794028> **{amount}** on **{user_choice}**\n"
                        f"The coin spins... **{result_emoji}** and you lost it all..."
            )

        reminders_json = load_json(REMINDERS_FILE)
        user_reminders = reminders_json.get(user_id, {})
        if user_reminders.get("coinflip", False):
            cooldown = coinflip_cooldown(ctx)
            self.reminders[user_id] = {
                "end": time.time() + cooldown.per,
                "channel": ctx.channel.id,
                "message": message.id
            }

    @coinflip.error
    async def coinflip_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_seconds = int(error.retry_after) 
            cooldown_text = "3 seconds" if is_premium(ctx.author.id) else "15 seconds"
            retry_time = int(time.time() + error.retry_after)
            embed = discord.Embed(
                title="<:ap_time:1382729675616555029> Slow Down!",
                description=(
                    f"You'll be able to use this command again <t:{retry_time}:R>\n\n"
                    f"The **default** cooldown is `15 seconds`\n"
                    f"The **premium** cooldown is `3 seconds`"
                ),
                color=discord.Color.default()
            )
            embed.set_footer(text=f"Remaining: {remaining_seconds}s ({cooldown_text})")
            await ctx.send(embed=embed, delete_after=6)

        elif isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument)):
            await ctx.send(
                f"<:ac_crossmark:1399650396322005002> Invalid format! The correct usage is:\n"
                f"`{ctx.prefix}cf <amount> <choice>`\n"
                f"Example: `{ctx.prefix}cf 100 heads`"
            )
        else:
            print(f"Unexpected error in command {ctx.command}: {error}")

    @tasks.loop(seconds=1)
    async def reminder_loop(self):
        now = time.time()
        to_remove = []

        for user_id, data in self.reminders.items():
            if now >= data["end"]:
                try:
                    channel = self.bot.get_channel(data["channel"])
                    msg = await channel.fetch_message(data["message"])
                    await msg.reply(f"<@{user_id}>, your `coinflip` cooldown is ready!")
                except Exception as e:
                    print(f"Coinflip reminder error: {e}")
                to_remove.append(user_id)

        for user_id in to_remove:
            self.reminders.pop(user_id, None)

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Coinflip(bot))
