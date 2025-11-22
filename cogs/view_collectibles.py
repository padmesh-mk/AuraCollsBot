import discord
from discord.ext import commands
from discord import app_commands
import json

# Load data from JSON files
def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

collectibles_data = load_json("collectibles.json")
info_data = load_json("collectible_info.json")
restricted_data = load_json("restrictedcoll.json")
tradable_data = load_json("tradablecoll.json")
orbs_data = load_json("orbs.json")    
orb_info = load_json("orb.json")     

class ViewCollectible(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_collectible_details(self, name: str):
        name = name.lower()
        for data_source, source_type in [
            (info_data, "info"),
            (restricted_data, "restricted"),
            (tradable_data, "tradable")
        ]:
            for key, value in data_source.items():
                if key.lower() == name or value["name"].lower() == name:
                    return key, value, source_type
        return None, None, None

    def get_user_count(self, user_id: int, coll_key: str):
        user_data = collectibles_data.get(str(user_id), {})
        return user_data.get(coll_key, 0)

    def build_embed(self, user: discord.User, key: str, details: dict, source_type: str, count: int):
        emoji = details.get("emoji", "❓")
        display_name = details.get("name", key)

        embed = discord.Embed(
            title=f"{emoji} {display_name}",
            color=0xFF6B6B
        )
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        embed.add_field(name="Owned", value=f"`{count}`", inline=True)

        if source_type == "info":
            embed.add_field(name="Source", value=details.get("source", "Unknown"), inline=False)
        elif source_type == "restricted":
            owner_id = details.get("owner_id")
            embed.add_field(name="Source", value=f"You can only receive this collectible from <@{owner_id}>", inline=False)
        elif source_type == "tradable":
            embed.add_field(name="Source", value="You can trade this collectible with others.", inline=False)

        cooldown = details.get("cooldown")
        if cooldown:
            embed.add_field(name="Cooldown", value=f"{cooldown} seconds", inline=True)

        return embed

    def get_orb_details(self, name: str):
        name = name.lower()
        for key, value in orb_info.items():
            if key.lower() == name or value["name"].lower() == name:
                return key, value
        return None, None

    def get_user_orb_count(self, user_id: int, orb_key: str):
        user_orbs = orbs_data.get(str(user_id), {})
        return user_orbs.get(orb_key, 0)

    def build_orb_embed(self, user: discord.User, key: str, details: dict, count: int):
        emoji = details.get("emoji", "❓")
        display_name = details.get("name", key)

        embed = discord.Embed(
            title=f"{emoji} {display_name}",
            color=0xFF6B6B
        )
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        embed.add_field(name="Owned", value=f"`{count}`", inline=True)
        embed.add_field(name="Source", value="You can get orbs from monthly event drops. (Not tradable)", inline=False)
        return embed

    @app_commands.command(name="view", description="View details about a collectible or orb")
    @app_commands.describe(item="Name of the collectible or orb")
    async def view_slash(self, interaction: discord.Interaction, item: str):
        key, details, source_type = self.get_collectible_details(item)
        if details:
            count = self.get_user_count(interaction.user.id, key)
            embed = self.build_embed(interaction.user, key, details, source_type, count)
            return await interaction.response.send_message(embed=embed)

        key, details = self.get_orb_details(item)
        if details:
            count = self.get_user_orb_count(interaction.user.id, key)
            embed = self.build_orb_embed(interaction.user, key, details, count)
            return await interaction.response.send_message(embed=embed)

        await interaction.response.send_message(
            "<:ap_crossmark:1382760353904988230> | That collectible or orb does not exist.", ephemeral=True
        )

    @commands.command(name="view")
    async def view_prefix(self, ctx, *, item: str = None):
        if not item:
            return await ctx.send("<:ap_crossmark:1382760353904988230> | Please provide a collectible or orb name to view.")

        key, details, source_type = self.get_collectible_details(item)
        if details:
            count = self.get_user_count(ctx.author.id, key)
            embed = self.build_embed(ctx.author, key, details, source_type, count)
            return await ctx.send(embed=embed)

        key, details = self.get_orb_details(item)
        if details:
            count = self.get_user_orb_count(ctx.author.id, key)
            embed = self.build_orb_embed(ctx.author, key, details, count)
            return await ctx.send(embed=embed)

        await ctx.send("<:ap_crossmark:1382760353904988230> | That collectible or orb does not exist.")

async def setup(bot):
    await bot.add_cog(ViewCollectible(bot))
