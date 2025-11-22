import discord
from discord.ext import commands
from discord import app_commands
import json
import os

COLLECTIBLES_FILE = "collectibles.json"
INFO_FILES = ["tradablecoll.json", "restrictedcoll.json", "collectible_info.json"]

def load_collectible_info():
    data = {}
    for file in INFO_FILES:
        if os.path.exists(file):
            with open(file, "r") as f:
                data.update(json.load(f))
    return data

def load_collectibles():
    if not os.path.exists(COLLECTIBLES_FILE):
        return {}
    with open(COLLECTIBLES_FILE, "r") as f:
        return json.load(f)

def get_coll_leaderboard(coll_name, guild: discord.Guild = None):
    collectibles = load_collectibles()
    leaderboard = []

    for user_id, user_data in collectibles.items():
        count = user_data.get(coll_name, 0)
        if count > 0:
            if guild and not guild.get_member(int(user_id)):
                continue
            leaderboard.append((user_id, {"count": count}))

    leaderboard.sort(key=lambda x: x[1]["count"], reverse=True)
    return leaderboard

def get_user_coll_data(user_id, coll_name, leaderboard):
    for rank, (uid, info) in enumerate(leaderboard, start=1):
        if str(uid) == str(user_id):
            return {"count": info["count"], "rank": rank}
    return {"count": 0, "rank": "N/A"}


class CollLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coll_info = load_collectible_info()

    async def coll_name_autocomplete(self, interaction: discord.Interaction, current: str):
        choices = []
        for name, info in self.coll_info.items():
            if current.lower() in name.lower():
                emoji = info.get("emoji", "❔")
                choices.append(app_commands.Choice(name=f"{emoji} {name}", value=name))
        return choices[:25]

    @commands.hybrid_command(name="colllb", description="Show collectibles leaderboard")
    @discord.app_commands.describe(coll_name="Name of the collectible")
    @discord.app_commands.autocomplete(coll_name=coll_name_autocomplete)
    async def colllb(self, ctx, coll_name: str):
        coll_name = coll_name.lower()
        if coll_name not in self.coll_info:
            return await ctx.send(f"<:ac_crossmark:1399650396322005002> Collectible `{coll_name}` not found.")

        lb = get_coll_leaderboard(coll_name)
        await self.show_page(ctx, coll_name, lb, 0, scope="global")

    async def show_page(self, ctx_or_interaction, coll_name, leaderboard, page: int, scope: str):
        PER_PAGE = 10
        total_pages = (len(leaderboard) + PER_PAGE - 1) // PER_PAGE or 1
        page = max(0, min(page, total_pages - 1))
        start = page * PER_PAGE
        end = start + PER_PAGE

        if isinstance(ctx_or_interaction, commands.Context):
            user = ctx_or_interaction.author
        else:
            user = ctx_or_interaction.user

        coll_emoji = self.coll_info.get(coll_name, {}).get("emoji", "❔")

        embed = discord.Embed(
            title=f"{coll_emoji} {coll_name.capitalize()} Leaderboard ({scope.title()})",
            color=0xFF6B6B
        )

        user_data = get_user_coll_data(user.id, coll_name, leaderboard)
        embed.description = f"{user.name}: `{user_data['count']}` | Rank: `#{user_data['rank']}`\n\n"

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        leaderboard_lines = []

        for idx, (user_id, info) in enumerate(leaderboard[start:end], start=start + 1):
            emoji = emoji_map.get(idx, f"#{idx}")
            count = info["count"]
            member = self.bot.get_user(int(user_id))
            username = member.name if member else f"{user_id}"
            leaderboard_lines.append(f"{emoji}  `{count}` – {username}")

        if leaderboard_lines:
            embed.add_field(name="Top Collectors", value="\n".join(leaderboard_lines), inline=False)
        else:
            embed.add_field(name="Top Collectors", value="No data found.", inline=False)

        embed.set_footer(text=f"Page {page+1}/{total_pages}")

        view = CollLeaderboardPaginator(self, coll_name, leaderboard, page, scope)

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(embed=embed, view=view)
        else:
            await ctx_or_interaction.followup.send(embed=embed, view=view, ephemeral=False)


class CollLeaderboardPaginator(discord.ui.View):
    def __init__(self, cog: CollLeaderboard, coll_name, leaderboard, current_page, scope):
        super().__init__(timeout=60)
        self.cog = cog
        self.coll_name = coll_name
        self.leaderboard = leaderboard
        self.page = current_page
        self.scope = scope

    @discord.ui.button(emoji="<:ap_backward:1382775479202746378>", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        await self.update(interaction)

    @discord.ui.button(emoji="<:ap_forward:1382775383371419790>", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = min(self.page + 1, (len(self.leaderboard) + 9) // 10 - 1)
        await self.update(interaction)

    @discord.ui.select(
        placeholder="Choose scope",
        options=[
            discord.SelectOption(label="Global", value="global"),
            discord.SelectOption(label="Guild", value="guild"),
        ]
    )
    async def scope_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        scope = select.values[0]
        guild = interaction.guild if scope == "guild" else None
        self.leaderboard = get_coll_leaderboard(self.coll_name, guild)
        self.page = 0
        self.scope = scope
        await self.update(interaction)

    async def update(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = await self.build_embed(interaction)
        await interaction.message.edit(embed=embed, view=self)

    async def build_embed(self, interaction):
        PER_PAGE = 10
        total_pages = (len(self.leaderboard) + PER_PAGE - 1) // PER_PAGE or 1
        page = max(0, min(self.page, total_pages - 1))
        start = page * PER_PAGE
        end = start + PER_PAGE

        user = interaction.user
        coll_emoji = self.cog.coll_info.get(self.coll_name, {}).get("emoji", "❔")

        embed = discord.Embed(
            title=f"{coll_emoji} {self.coll_name.capitalize()} Leaderboard ({self.scope.title()})",
            color=discord.Color.orange()
        )
        user_data = get_user_coll_data(user.id, self.coll_name, self.leaderboard)
        embed.description = f"{user.name}: `{user_data['count']}` | Rank: `#{user_data['rank']}`\n\n"

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        leaderboard_lines = []

        for idx, (user_id, info) in enumerate(self.leaderboard[start:end], start=start + 1):
            emoji = emoji_map.get(idx, f"#{idx}")
            count = info["count"]
            member = self.cog.bot.get_user(int(user_id))
            username = member.name if member else f"{user_id}"
            leaderboard_lines.append(f"{emoji}  `{count}` – {username}")

        if leaderboard_lines:
            embed.add_field(name="Top Collectors", value="\n".join(leaderboard_lines), inline=False)
        else:
            embed.add_field(name="Top Collectors", value="No data found.", inline=False)

        embed.set_footer(text=f"Page {page+1}/{total_pages}")
        return embed

async def setup(bot):
    await bot.add_cog(CollLeaderboard(bot))
