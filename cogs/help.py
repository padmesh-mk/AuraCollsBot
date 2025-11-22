import discord
from discord.ext import commands
from discord import app_commands

class HelpMenu(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=60)
        self.author = author
        self.current_page = 1
        self.total_pages = 7

    async def update_message(self, interaction: discord.Interaction):
        embed = self.get_embed_for_page(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)

    def get_embed_for_page(self, page: int):
        embed = discord.Embed(color=0xFF6B6B)
        embed.timestamp = discord.utils.utcnow()

        if page == 1:
            embed.title = 'General Commands'
            embed.description = (
                '`abotinfo` • </botinfo:1398640701217968248>\n⤷ Shows info about bot.\n'
                '`aguide` • </guide:1415291110070161481>\n⤷ Shows guide about using the bot for starters.\n'
                '`ahelp` • </help:1403033840913743993>\n⤷ Shows this help menu.\n'
                '`apremium` • </premium:1409937275927924836>\n⤷ To buy Premium.\n'
                '`aping` • </ping:1398631017002041469>\n⤷ Shows latency info\n'
                '`auptime` • </uptime:1398640701217968249>\n⤷ Check the uptime of bot.\n'
                '`avote | av` • </vote:1405159389962178580>\n⤷ Vote for the bot.\n'
                '`ainvite` • </invite:1406971621100753019>\n⤷ Get the invite link.'
            )
        elif page == 2:
            embed.title = 'General Commands-2'
            embed.description = (
                '`aprofile` • </profile:1412350084749983836>\n⤷ Shows an user profile.\n'
                '`ashowcase add` • </showcase add:1412122923044573388>\n⤷ To add an collectible to profile.\n'
                '`ashowcase remove` • </showcase remove:1412122923044573388>\n⤷ To remove an collectible from profile.\n'
                '`amarry` • </marry:1407058811092471949>\n⤷ Propose to an user with a ring.\n'
                '`amarriage | am` • </marriage:1407058811092471950>\n⤷ Check your marriage status.\n'
                '`adivorce` • </divorce:1407058811092471951>\n⤷ Divorce your partner.'
            )
        elif page == 3:
            embed.title = 'Economy Commands'
            embed.description = (
                '`adaily` • </daily:1399446954852880396>\n⤷ Claim daily coins and collectible.\n'
                '`aweekly` • </weekly:1408516300946280530>\n⤷ Claim weekly coins and collectible.\n'
                '`acoins | acoin` • </coins:1406971621100753017>\n⤷ Check your coins.\n'
                '`ashop` • </shop:1404004604768813066>\n⤷ Purchace collectibles with your coins.\n'
                '`agive | asend`\n⤷ Give your coins to someone.\n'
                '`acoinflip | acf`\n⤷ Gamble you coins using Coinflip.\n'
                '`awork` • </work:1426193173423718430>\n⤷ Work to earn coins or collectibles.\n'
                '`aevent` • </event:1427265883813974066>\n⤷ Check the current Event details.\n'
                '`apick` • </pick:1427223508542427241>\n⤷ Pick to get items during an Event.'
            )
        elif page == 4:
            embed.title = 'Collectible Commands'
            embed.description = (
                '`alist` • </list:1399479675914551316>\n⤷ List all collectibles.\n'
                '`aorb | aorbs` • </orb:1427223508542427240>\n⤷ List all orbs.\n'
                '`aview` • </view:1399622324214431878>\n⤷ View info about a specific collectible.\n'
                '`acompare` • </compare:1399631935680020502>\n⤷ Compare collectibles with other user.\n'
                '`abundle list` • </bundle view:1409593612513181851>\n⤷ View available bundles.\n'
                '`abundle claim` • </bundle claim:1409593612513181851>\n⤷ Claim a bundle reward.\n'
                '`areminders` • </reminders:1409959290046775477>\n⤷ Enable/disable reminders for certain functions.'
            )
        elif page == 5:
            embed.title = 'Leaderboard Commands'
            embed.description = (
                '`adailylb` • </dailylb:1399450665385984132>\n⤷ Show the top daily streak leaderboard.\n'
                '`acoinslb` • </coinslb:1406971621100753018>\n⤷ Show the top coins leaderboard.\n'
                '`avotelb` • </votelb:1399263970992455752>\n⤷ Show the top voters leaderboard.\n'
                '`acolllb <coll_name>` • </colllb:1415258264634920990>\n⤷ Show leaderboard for each collectibles.'
            )
        elif page == 6:
            embed.title = 'Text Action Commands'
            embed.description = (
                '`awave`\n⤷ Wave to someone.\n'
                '`abonk`\n⤷ Bonks someone in the head.\n'
                '`abully`\n⤷ Bully someone.\n'
                '`ahug`\n⤷ Give someone a hug.\n'
                '`akill`\n⤷ Virtually eliminate someone...\n'
                '`akiss`\n⤷ Send a sweet kiss to someone.\n'
                '`apat`\n⤷ Pat someone gently.\n'
                '`aslap`\n⤷ Give someone a playful slap.\n'
                '`aship` • </ship:1407744876778356777>\n⤷ Ship with someone.'
            )            
        elif page == 7:
            embed.title = 'Admin Commands'
            embed.description = (
                '`aprefix list` • </prefix list:1398631017002041468>\n⤷ Show the current prefixes.\n'
                '`aprefix add` • </prefix add:1398631017002041468>\n⤷ Add an new prefix.\n'
                '`aprefix remove` • </prefix remove:1398631017002041468>\n⤷ Remove an existing prefix.'
            )

        embed.set_footer(text=f"Page {page} of {self.total_pages}")
        return embed

    @discord.ui.button(emoji='<:ap_backward:1382775479202746378>', style=discord.ButtonStyle.secondary, custom_id="back")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This menu isn't for you.", ephemeral=True)
        if self.current_page > 1:
            self.current_page -= 1
            await self.update_message(interaction)

    @discord.ui.button(emoji='<:ap_forward:1382775383371419790>', style=discord.ButtonStyle.secondary, custom_id="forward")
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This menu isn't for you.", ephemeral=True)
        if self.current_page < self.total_pages:
            self.current_page += 1
            await self.update_message(interaction)

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_prefix(self, ctx):
        view = HelpMenu(ctx.author)
        embed = view.get_embed_for_page(1)
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="help", description="Displays a help menu with information about commands.")
    async def help_slash(self, interaction: discord.Interaction):
        view = HelpMenu(interaction.user)
        embed = view.get_embed_for_page(1)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
