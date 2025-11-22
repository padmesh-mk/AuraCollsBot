import discord
from discord.ext import commands
import random
import json
import os

KISS_FILE = "kiss.json"

class Kiss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kiss_data = self.load_kiss_data()

    def load_kiss_data(self):
        if os.path.exists(KISS_FILE):
            with open(KISS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"default": [], "self": [], "self_mention": [], "bot": []}

    @commands.command(name="kiss")
    async def kiss(self, ctx, member: discord.Member = None):
        sender = ctx.author

        if member is None:
            return await ctx.send(random.choice(self.kiss_data["self"]).format(sender=sender.mention))

        if member.id == sender.id:
            return await ctx.send(random.choice(self.kiss_data["self_mention"]).format(sender=sender.mention))

        if member.id == self.bot.user.id:
            return await ctx.send(random.choice(self.kiss_data["bot"]).format(sender=sender.mention))

        phrase = random.choice(self.kiss_data["default"]).format(sender=sender.mention, target=member.mention)
        await ctx.send(phrase)

async def setup(bot):
    await bot.add_cog(Kiss(bot))
