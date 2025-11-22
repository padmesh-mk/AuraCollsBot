import discord
from discord.ext import commands
import random
import json
import os

KILL_FILE = "kill.json"

class Kill(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kill_data = self.load_kill_data()

    def load_kill_data(self):
        if os.path.exists(KILL_FILE):
            with open(KILL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"default": [], "self": [], "self_mention": [], "bot": []}

    @commands.command(name="kill")
    async def kill(self, ctx, member: discord.Member = None):
        sender = ctx.author

        if member is None and ctx.message.reference:
            try:
                replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                if replied_message and replied_message.author != sender:
                    member = replied_message.author
            except:
                pass

        if member is None:
            return await ctx.send(random.choice(self.kill_data["self"]).format(sender=sender.mention))

        if member.id == sender.id:
            return await ctx.send(random.choice(self.kill_data["self_mention"]).format(sender=sender.mention))

        if member.id == self.bot.user.id:
            return await ctx.send(random.choice(self.kill_data["bot"]).format(sender=sender.mention))

        phrase = random.choice(self.kill_data["default"]).format(sender=sender.mention, target=member.mention)
        await ctx.send(phrase)

async def setup(bot):
    await bot.add_cog(Kill(bot))
