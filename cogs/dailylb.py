import discord
from discord.ext import commands
import json
import os

DAILY_FILE = "daily.json"

<<<<<<< HEAD
def get_daily_leaderboard(guild: discord.Guild = None):
=======
def get_daily_leaderboard():
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
    if not os.path.exists(DAILY_FILE):
        return []

    with open(DAILY_FILE, "r") as f:
        data = json.load(f)

    sorted_data = sorted(data.items(), key=lambda x: x[1].get("streak", 0), reverse=True)
    leaderboard = []
    for user_id, info in sorted_data:
<<<<<<< HEAD
        if guild and not guild.get_member(int(user_id)):
            continue
        leaderboard.append((user_id, {"streak": info.get("streak", 0)}))
    return leaderboard

def get_user_daily_data(user_id, leaderboard):
=======
        leaderboard.append((user_id, {"streak": info.get("streak", 0)}))
    return leaderboard

def get_user_daily_data(user_id):
    leaderboard = get_daily_leaderboard()
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
    for rank, (uid, info) in enumerate(leaderboard, start=1):
        if str(uid) == str(user_id):
            return {"streak": info["streak"], "rank": rank}
    return {"streak": 0, "rank": "N/A"}

class DailyLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

<<<<<<< HEAD
    @commands.hybrid_command(
        name="dailylb",
        description="Show the top daily claimers leaderboard",
        aliases=["daily lb"]
    )
    async def dailylb(self, ctx):
        lb = get_daily_leaderboard()
        await self.show_page(ctx, lb, 0, scope="global")

    async def show_page(self, ctx_or_interaction, leaderboard, page: int, scope: str):
        PER_PAGE = 10
        total_pages = (len(leaderboard) + PER_PAGE - 1) // PER_PAGE or 1
=======
    @commands.hybrid_command(name="dailylb", description="Show the top daily claimers leaderboard", aliases=["daily lb"])
    async def dailylb(self, ctx):
        lb = get_daily_leaderboard()
        await self.show_page(ctx, lb, 0)

    async def show_page(self, ctx_or_interaction, leaderboard, page: int):
        PER_PAGE = 10
        total_pages = (len(leaderboard) + PER_PAGE - 1) // PER_PAGE
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
        page = max(0, min(page, total_pages - 1))
        start = page * PER_PAGE
        end = start + PER_PAGE

        if isinstance(ctx_or_interaction, commands.Context):
            user = ctx_or_interaction.author
        else:
            user = ctx_or_interaction.user

        embed = discord.Embed(
<<<<<<< HEAD
            title=f"<:ap_chart:1384942967642394654> Daily Leaderboard ({scope.title()})",
            color=0xFF6B6B
        )

        user_data = get_user_daily_data(user.id, leaderboard)
=======
            title="<:ap_daily:1395624067648720998> Global Daily Leaderboard",
            color=0xFF6B6B
        )

        user_data = get_user_daily_data(user.id)
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
        embed.description = f"{user.name}: `{user_data['streak']}` | Rank: `#{user_data['rank']}`\n\n"

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        leaderboard_lines = []

        for idx, (user_id, info) in enumerate(leaderboard[start:end], start=start + 1):
            emoji = emoji_map.get(idx, f"#{idx}")
            streak = info["streak"]
            member = self.bot.get_user(int(user_id))
            username = member.name if member else f"{user_id}"
            leaderboard_lines.append(f"{emoji}  `{streak}` – {username}")

<<<<<<< HEAD
        if leaderboard_lines:
            embed.add_field(name="Top Daily Claimers", value="\n".join(leaderboard_lines), inline=False)
        else:
            embed.add_field(name="Top Daily Claimers", value="No data found.", inline=False)

        embed.set_footer(text=f"Page {page+1}/{total_pages}")

        view = DailyLeaderboardPaginator(self, leaderboard, page, scope)
=======
        embed.add_field(name="Top Daily Claimers", value="\n".join(leaderboard_lines), inline=False)
        embed.set_footer(text=f"Page {page+1}/{total_pages}")

        view = DailyLeaderboardPaginator(self, leaderboard, page)
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(embed=embed, view=view)
        else:
            await ctx_or_interaction.followup.send(embed=embed, view=view, ephemeral=False)

<<<<<<< HEAD

class DailyLeaderboardPaginator(discord.ui.View):
    def __init__(self, cog: DailyLeaderboard, leaderboard, current_page, scope):
=======
class DailyLeaderboardPaginator(discord.ui.View):
    def __init__(self, cog: DailyLeaderboard, leaderboard, current_page):
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
        super().__init__(timeout=60)
        self.cog = cog
        self.leaderboard = leaderboard
        self.page = current_page
<<<<<<< HEAD
        self.scope = scope
=======
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47

    @discord.ui.button(emoji="<:ap_backward:1382775479202746378>", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        await self.update(interaction)

    @discord.ui.button(emoji="<:ap_forward:1382775383371419790>", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = min(self.page + 1, (len(self.leaderboard) + 9) // 10 - 1)
        await self.update(interaction)

<<<<<<< HEAD
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
        self.leaderboard = get_daily_leaderboard(guild)
        self.page = 0
        self.scope = scope
        await self.update(interaction)

=======
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
    async def update(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = await self.build_embed(interaction)
        await interaction.message.edit(embed=embed, view=self)

    async def build_embed(self, interaction):
        PER_PAGE = 10
<<<<<<< HEAD
        total_pages = (len(self.leaderboard) + PER_PAGE - 1) // PER_PAGE or 1
=======
        total_pages = (len(self.leaderboard) + PER_PAGE - 1) // PER_PAGE
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
        page = max(0, min(self.page, total_pages - 1))
        start = page * PER_PAGE
        end = start + PER_PAGE

        user = interaction.user
<<<<<<< HEAD
        user_data = get_user_daily_data(user.id, self.leaderboard)

        embed = discord.Embed(
            title=f"<:ap_chart:1384942967642394654> Daily Leaderboard ({self.scope.title()})",
=======
        user_data = get_user_daily_data(user.id)

        embed = discord.Embed(
            title="<:ap_daily:1395624067648720998> Global Daily Leaderboard",
>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
            color=discord.Color.orange()
        )
        embed.description = f"{user.name}: `{user_data['streak']}` | Rank: `#{user_data['rank']}`\n\n"

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        leaderboard_lines = []

        for idx, (user_id, info) in enumerate(self.leaderboard[start:end], start=start + 1):
            emoji = emoji_map.get(idx, f"#{idx}")
            streak = info["streak"]
            member = self.cog.bot.get_user(int(user_id))
            username = member.name if member else f"{user_id}"
            leaderboard_lines.append(f"{emoji}  `{streak}` – {username}")

<<<<<<< HEAD
        if leaderboard_lines:
            embed.add_field(name="Top Daily Claimers", value="\n".join(leaderboard_lines), inline=False)
        else:
            embed.add_field(name="Top Daily Claimers", value="No data found.", inline=False)

        embed.set_footer(text=f"Page {page+1}/{total_pages}")
        return embed


=======
        embed.add_field(name="Top Daily Claimers", value="\n".join(leaderboard_lines), inline=False)
        embed.set_footer(text=f"Page {page+1}/{total_pages}")
        return embed

>>>>>>> fc0bbefadbbd3ed7bedc2f1ec1bc2d359c6d9c47
async def setup(bot):
    await bot.add_cog(DailyLeaderboard(bot))
