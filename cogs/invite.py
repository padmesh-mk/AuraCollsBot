import discord
from discord.ext import commands

INVITE_URL = "https://discord.com/oauth2/authorize?client_id=1261363542867578910"
SUPPORT_SERVER = "https://discord.gg/becvfQ9fCr"

class Invite(commands.Cog):
    """Get invite link of AuraColls Bot and Support server."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="invite")
    async def invite_cmd(self, ctx):
        embed = discord.Embed(
            title="Thank you for choosing AuraColls!",
            color=discord.Color.from_str("#ff6b6b")
        )
        embed.add_field(name="<:ap_invite:1382717191052328961> Invite AuraColls", value=f"[Click here]({INVITE_URL})", inline=False)
        embed.add_field(name="<:ap_support:1382716862256910437> Support Server", value=f"[Join here]({SUPPORT_SERVER})", inline=False)
        embed.set_footer(text="We appreciate your support!")
        await ctx.send(embed=embed)

    @discord.app_commands.command(name="invite", description="Get the bot's invite and support server link.")
    async def invite_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Thank you for choosing AuraColls!",
            color=discord.Color.from_str("#ff6b6b")
        )
        embed.add_field(name="<:ap_invite:1382717191052328961> Invite AuraColls", value=f"[Click here]({INVITE_URL})", inline=False)
        embed.add_field(name="<:ap_support:1382716862256910437> Support Server", value=f"[Join here]({SUPPORT_SERVER})", inline=False)
        embed.set_footer(text="We appreciate your support!")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Invite(bot))
