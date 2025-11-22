import discord
from discord.ext import commands
import json
import os

POINTS_FILE = "coins.json"

def get_points_leaderboard(guild: discord.Guild = None):
    if not os.path.exists(POINTS_FILE):
        return []

    with open(POINTS_FILE, "r") as f:
        data = json.load(f)

    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    leaderboard = []
    for user_id, points in sorted_data:
        if guild and not guild.get_member(int(user_id)):
            continue
        leaderboard.append((user_id, {"coins": points}))
    return leaderboard

def get_user_point_data(user_id, leaderboard):
    for rank, (uid, info) in enumerate(leaderboard, start=1):
        if str(uid) == str(user_id):
            return {"coins": info["coins"], "rank": rank}
    return {"coins": 0, "rank": "N/A"}


class PointsLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="coinslb",
        description="Show the top coins leaderboard",
        aliases=["coinlb"]
    )
    async def pointslb(self, ctx):
        lb = get_points_leaderboard()
        await self.show_page(ctx, lb, 0, scope="global")

    async def show_page(self, ctx_or_interaction, leaderboard, page: int, scope: str):
        PER_PAGE = 10
        total_pages = (len(leaderboard) + PER_PAGE - 1) // PER_PAGE or 1
        page = max(0, min(page, total_pages - 1))
        start = page * PER_PAGE
        end = start + PER_PAGE

        if isinstance(ctx_or_interaction, commands.Context):
            user = ctx_or_interaction.author
        else:
            user = ctx_or_interaction.user

        embed = discord.Embed(
            title=f"<:ac_coins:1400522330668794028> Coins Leaderboard ({scope.title()})",
            color=0xFF6B6B
        )

        user_data = get_user_point_data(user.id, leaderboard)
        embed.description = f"{user.name}: `{user_data['coins']:,}` | Rank: `#{user_data['rank']}`\n\n"

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        leaderboard_lines = []

        for idx, (user_id, info) in enumerate(leaderboard[start:end], start=start + 1):
            emoji = emoji_map.get(idx, f"#{idx}")
            points = info["coins"]
            formatted_points = f"{points:,}"
            member = self.bot.get_user(int(user_id))
            username = member.name if member else f"{user_id}"
            leaderboard_lines.append(f"{emoji}  `{formatted_points}` – {username}")

        if leaderboard_lines:
            embed.add_field(name="Top Coins Ranking", value="\n".join(leaderboard_lines), inline=False)
        else:
            embed.add_field(name="Top Coins Ranking", value="No data found.", inline=False)

        embed.set_footer(text=f"Page {page+1}/{total_pages}")

        view = PointsLeaderboardPaginator(self, leaderboard, page, scope)

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(embed=embed, view=view)
        else:
            await ctx_or_interaction.followup.send(embed=embed, view=view, ephemeral=False)


class PointsLeaderboardPaginator(discord.ui.View):
    def __init__(self, cog: PointsLeaderboard, leaderboard, current_page, scope):
        super().__init__(timeout=60)
        self.cog = cog
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
        self.leaderboard = get_points_leaderboard(guild)
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
        user_data = get_user_point_data(user.id, self.leaderboard)

        embed = discord.Embed(
            title=f"<:ap_chart:1384942967642394654> Coins Leaderboard ({self.scope.title()})",
            color=discord.Color.orange()
        )
        embed.description = f"{user.name}: `{user_data['coins']:,}` | Rank: `#{user_data['rank']}`\n\n"

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        leaderboard_lines = []

        for idx, (user_id, info) in enumerate(self.leaderboard[start:end], start=start + 1):
            emoji = emoji_map.get(idx, f"#{idx}")
            points = info["coins"]
            formatted_points = f"{points:,}"
            member = self.cog.bot.get_user(int(user_id))
            username = member.name if member else f"{user_id}"
            leaderboard_lines.append(f"{emoji}  `{formatted_points}` – {username}")

        if leaderboard_lines:
            embed.add_field(name="Top Coins Ranking", value="\n".join(leaderboard_lines), inline=False)
        else:
            embed.add_field(name="Top Coins Ranking", value="No data found.", inline=False)

        embed.set_footer(text=f"Page {page+1}/{total_pages}")
        return embed


async def setup(bot):
    await bot.add_cog(PointsLeaderboard(bot))
