import discord
from discord.ext import commands
from discord.ui import View, Button
import math

OWNER_ID = 941902212303556618 

class ServerListView(View):
    """Show the list of servers (restricted to owner-only)."""
    def __init__(self, bot, entries, author):
        super().__init__(timeout=60)
        self.bot = bot
        self.entries = sorted(entries, key=lambda g: g.member_count or 0, reverse=True)
        self.author = author
        self.page = 0
        self.total_pages = math.ceil(len(self.entries) / 10)

        self.prev_button = Button(label="Previous", style=discord.ButtonStyle.blurple)
        self.next_button = Button(label="Next", style=discord.ButtonStyle.blurple)
        self.extra_button = Button(label="Extra Info", style=discord.ButtonStyle.danger)

        self.prev_button.callback = self.go_previous
        self.next_button.callback = self.go_next
        self.extra_button.callback = self.show_extra_info

        self.add_item(self.prev_button)
        self.add_item(self.next_button)
        self.add_item(self.extra_button)

    def get_embed(self):
        start = self.page * 10
        end = start + 10
        total_members = sum(guild.member_count or 0 for guild in self.entries)
        embed = discord.Embed(
            title="<:ap_server:1382719087221674115> Server List",
            color=0xFF6B6B
        )

        for i, guild in enumerate(self.entries[start:end], start=start + 1):
            embed.add_field(
                name=f"{i}. {guild.name}",
                value=f"Members: `{guild.member_count}`",
                inline=False
            )

        embed.set_footer(
            text=f"Page [{self.page + 1}/{self.total_pages}] • Total Servers: {len(self.entries)} • Total Members: {total_members}"
        )
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("You can't interact with this view.", ephemeral=True)
            return False
        return True

    async def go_previous(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    async def go_next(self, interaction: discord.Interaction):
        if self.page < self.total_pages - 1:
            self.page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    async def show_extra_info(self, interaction: discord.Interaction):
        start = self.page * 10
        end = start + 10
        guilds = self.entries[start:end]
        info = "\n".join(f"**{guild.name}** - `{guild.id}`" for guild in guilds)
        await interaction.response.send_message(f"Extra Server Info:\n{info}", ephemeral=True)

class ServerList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="serverlist", description="List all servers the bot is in. (Owner only)")
    async def serverlist(self, ctx: commands.Context):
        if ctx.author.id != OWNER_ID:
            msg = "<:ap_crossmark:1382760353904988230> This command is owner-only."
            if isinstance(ctx, commands.Context):
                await ctx.send(msg)
            else:
                await ctx.interaction.response.send_message(msg, ephemeral=True)
            return

        entries = self.bot.guilds
        view = ServerListView(self.bot, entries, ctx.author)
        embed = view.get_embed()

        if isinstance(ctx, commands.Context):
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ServerList(bot))
