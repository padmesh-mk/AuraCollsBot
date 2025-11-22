import discord
from discord.ext import commands

OWNER_ID = 941902212303556618 

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="serverdetail")
    async def serverinfo(self, ctx, guild_id: int):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("<:ac_crossmark:1399650396322005002> This command is owner-only.")

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return await ctx.send("<:ac_crossmark:1399650396322005002> I'm not in that server or it's not cached.")

        invite_url = "<:ac_crossmark:1399650396322005002> Could not create invite"
        try:
            channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).create_instant_invite), None)
            if channel:
                invite = await channel.create_invite(max_age=3600, max_uses=1, unique=True)
                invite_url = invite.url
        except:
            pass

        embed = discord.Embed(
            title=f"Server Info: {guild.name}",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Owner ID", value=guild.owner_id, inline=False)
        embed.add_field(name="Members", value=guild.member_count, inline=False)
        embed.add_field(name="Invite", value=invite_url, inline=False)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
