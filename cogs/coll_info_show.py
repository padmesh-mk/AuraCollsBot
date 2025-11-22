import discord
from discord.ext import commands
import json
import os

class CollCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collectibles = self.load_json("collectibles.json")
        self.collectible_info = self.load_json("collectible_info.json")

    def load_json(self, filename):
        if not os.path.exists(filename):
            return {}
        with open(filename, "r") as f:
            return json.load(f)

    async def cog_load(self):
        for key in self.collectible_info.keys():
            self.bot.add_command(self.generate_command(key))

    def generate_command(self, collectible_name):
        @commands.command(name=collectible_name.lower())
        async def _command(ctx):
            with open("collectibles.json", "r") as f:
                collectibles = json.load(f)
            
            user_id = str(ctx.author.id)
            count = collectibles.get(user_id, {}).get(collectible_name, 0)
            emoji = self.collectible_info[collectible_name]["emoji"]
            name = self.collectible_info[collectible_name]["name"]

            await ctx.send(f"{emoji} **| {ctx.author.display_name}**, you currently have {count} {name}!")

        return _command

async def setup(bot):
    await bot.add_cog(CollCount(bot))
