import discord
from discord.ext import commands
from discord import app_commands

class GuideMenu(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=180)
        self.author = author
        self.current_page = 1
        self.total_pages = 7

    def get_embed_for_page(self, page: int):
        embed = discord.Embed(color=0xFF6B6B)
        embed.timestamp = discord.utils.utcnow()

        if page == 1:
            embed.title = "Welcome to AuraColls"
            embed.description = (
                "AuraColls is a collectible bot where you can collect, trade, and send unique items to other users.\n\n"
                "Use </list:1399479675914551316> or `alist` to view your collectibles"
            )
        elif page == 2:
            embed.title = "Collecting Items"
            embed.description = (
                "• Collectibles can be tradable or owner-only.\n"
                "• Tradable items can be freely sent to other users.\n"
                "• Owner-only items can be required from the owner of that collectible.\n"
                "• Use </view:1409595009761546256> or `aview <item>` to see details about a collectible."
            )
        elif page == 3:
            embed.title = "Sending Collectibles"
            embed.description = (
                "• Send collectibles using `a<coll_name> @user`.\n"
                "• Tradable items will duplicate among sharing with eachothers.\n"
                "• You gain **1 coin** whenever you send any collectible. (Premium users gain **2 coins** per trade)\n"
                "• Make sure you have enough items before sending!"
            )
        elif page == 4:
            embed.title = "Daily Rewards"
            embed.description = (
                "• Claim daily rewards using </daily:1399446954852880396> or `adaily`.\n"
                "• Receive random coins and a collectible.\n"
                "• Daily streaks are tracked and contribute to the leaderboard.\n"
                "• You can also claim </weekly:1412403432127594611> or `aweekly` every 7 days."
            )
        elif page == 5:
            embed.title = "Leaderboards"
            embed.description = (
                "• `/dailylb` – Top daily streaks.\n"
                "• `/coinslb` – Top points leaderboard.\n"
                "• `/votelb` – Top voters leaderboard.\n"
                "• `/colllb` – Specific collectible leaderboard.\n"
                "• Use dropdowns in leaderboards to switch between Global and Guild views."
            )
        elif page == 6:
            embed.title = "Shop"
            embed.description = (
                "• Access the shop with </shop:1412403432127594610> or `ashop`.\n"
                "• Buy tradable and restricted collectibles using points.\n"
                "• Shop resets daily at 9 AM IST."
            )
        elif page == 7:
            embed.title = "Need More Help?"
            embed.description = (
                "• Use </help:1403033840913743993> or `ahelp` to see all commands and their usage.\n"
                "• Join our Support Server for tips and assistance.\n"
                "• Read the #faq channel for common questions.\n"
                "• Open a support ticket if you need personal help.\n\n"
                "• **Support Server:** https://discord.gg/becvfQ9fCr"
            )


        embed.set_footer(text=f"Page {page} of {self.total_pages}")
        return embed

    @discord.ui.button(emoji="<:ap_backward:1382775479202746378>", style=discord.ButtonStyle.secondary, custom_id="back")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This guide isn't for you.", ephemeral=True)
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed_for_page(self.current_page), view=self)

    @discord.ui.button(emoji="<:ap_forward:1382775383371419790>", style=discord.ButtonStyle.secondary, custom_id="forward")
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This guide isn't for you.", ephemeral=True)
        if self.current_page < self.total_pages:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed_for_page(self.current_page), view=self)

class GuideCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="guide")
    async def guide_prefix(self, ctx):
        view = GuideMenu(ctx.author)
        embed = view.get_embed_for_page(1)
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="guide", description="Show a starter guide for AuraColls")
    async def guide_slash(self, interaction: discord.Interaction):
        view = GuideMenu(interaction.user)
        embed = view.get_embed_for_page(1)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(GuideCog(bot))
