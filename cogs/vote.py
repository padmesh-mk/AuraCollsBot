import discord
from discord.ext import commands
import json
import datetime
import asyncio

from votes import get_user_data, update_user_vote
from vote_remind import add_to_reminder

VOTE_WEBHOOK_CHANNEL_ID = 1419546088523829299
PUBLIC_LOG_CHANNEL_ID   = 1399256316370751488
PRIVATE_LOG_CHANNEL_ID  = 1399256437875540118
ROLE_REWARD_ID          = 1398017116359233647
VOTE_LINK               = "https://top.gg/bot/1261363542867578910/vote"
COLLECTIBLES_FILE       = "collectibles.json"

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.channel.id != VOTE_WEBHOOK_CHANNEL_ID:
            return

        content = message.content.strip()
        if not content.isdigit():
            return

        user_id = content

        try:
            await message.add_reaction("<:ap_checkmark:1382760062728273920>")
        except Exception:
            pass

        await self.process_vote(user_id, message.guild.id if message.guild else None, message)

    async def process_vote(self, user_id: str, guild_id: int = None, message=None):
        update_user_vote(user_id)
        add_to_reminder(user_id)

        try:
            with open(COLLECTIBLES_FILE, "r") as f:
                collectible_data = json.load(f)
        except FileNotFoundError:
            collectible_data = {}

        if user_id not in collectible_data:
            collectible_data[user_id] = {}

        collectible_data[user_id]["voter"] = collectible_data[user_id].get("voter", 0) + 1

        with open(COLLECTIBLES_FILE, "w") as f:
            json.dump(collectible_data, f, indent=4)

        try:
            with open("premium.json", "r") as f:
                premium_data = json.load(f)
        except FileNotFoundError:
            premium_data = {"users": {}}

        premium_user = premium_data.get("users", {}).get(user_id)
        gave_premium = False
        if premium_user:
            expiry = datetime.datetime.fromisoformat(premium_user.get("expiry"))
            if datetime.datetime.utcnow() < expiry: 
                try:
                    with open("currency.json", "r") as f:
                        coins_data = json.load(f)
                except FileNotFoundError:
                    coins_data = {}

                coins_data[user_id] = coins_data.get(user_id, 0) + 10

                with open("currency.json", "w") as f:
                    json.dump(coins_data, f, indent=4)
                gave_premium = True

        user_data = get_user_data(user_id)
        total_votes = user_data.get("votes", 0)
        rank = user_data.get("rank", "N/A")

        guild = self.bot.get_guild(guild_id) if guild_id else None
        member = guild.get_member(int(user_id)) if guild else None
        role = guild.get_role(ROLE_REWARD_ID) if guild else None

        if member and role:
            await member.add_roles(role, reason="Voted for AuraColls (12-hour reward)")

            async def remove_role_later():
                await asyncio.sleep(12 * 60 * 60)
                try:
                    await member.remove_roles(role, reason="Vote reward expired (12-hour)")
                except Exception as e:
                    print(f"Failed to remove vote role: {e}")

            self.bot.loop.create_task(remove_role_later())

        user = self.bot.get_user(int(user_id))
        if user:
            desc = (
                f"{user.mention}, thank you for voting! 🎉\n"
                f"You've received 1x <:ap_vote:1395506333834543144> **Voter** collectible!"
            )
            if gave_premium:
                desc += "\nPremium bonus reward: **10 Coins**"

            thank_embed = discord.Embed(
                description=desc,
                color=discord.Color.green()
            )
            try:
                await user.send(embed=thank_embed)
            except discord.Forbidden:
                print(f"Could not DM {user_id}")

        public_log = self.bot.get_channel(PUBLIC_LOG_CHANNEL_ID)
        if public_log and user:
            embed = discord.Embed(
                title="<:ap_vote:1395506333834543144> New Vote!",
                description=f"{user.mention} just voted for **AuraColls** on [Top.gg]({VOTE_LINK})\n"
                            f"**Total Votes:** `{total_votes}`",
                color=discord.Color.from_str("#ff6b6b"),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(text="Thank you for supporting us!")
            embed.set_thumbnail(url=user.display_avatar.url)
            await public_log.send(embed=embed)

        private_log = self.bot.get_channel(PRIVATE_LOG_CHANNEL_ID)
        if private_log and user:
            msg_id = message.id if message else "N/A"
            channel_id = message.channel.id if message else "N/A"
            guild_id = message.guild.id if message and message.guild else "N/A"
            msg_link = f"https://discord.com/channels/{guild_id}/{channel_id}/{msg_id}"

            embed = discord.Embed(
                title="📬 New Vote Logged",
                color = discord.Color(0xFFFFFF),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(name="User", value=f"{user.mention} (`{user.id}`)", inline=False)
            embed.add_field(name="Username", value=f"`{user.name}#{user.discriminator}`", inline=False)
            if guild:
                embed.add_field(name="Server", value=f"{guild.name} (`{guild.id}`)", inline=False)
            embed.add_field(name="Total Votes", value=f"`{total_votes}`", inline=True)
            embed.add_field(name="Rank", value=f"`#{rank}`", inline=True)
            embed.add_field(name="Message Link", value=f"[Jump to message]({msg_link})", inline=False)
            embed.set_footer(text="Private Vote Log")
            await private_log.send(embed=embed)

    @commands.hybrid_command(name="vote", description="Vote for the bot and check your stats", aliases=["v"])
    async def vote(self, ctx_or_inter):
        await self.handle_vote(ctx_or_inter)

    async def handle_vote(self, ctx_or_inter):
        user = ctx_or_inter.user if isinstance(ctx_or_inter, discord.Interaction) else ctx_or_inter.author
        user_id = str(user.id)

        user_data = get_user_data(user_id)
        last_vote_ts = user_data.get("last_vote", 0)
        total_votes = user_data.get("votes", 0)
        rank = user_data.get("rank", "N/A")
        last_vote = f"<t:{int(last_vote_ts)}:R>" if last_vote_ts else "Never"

        embed = discord.Embed(
            title="<a:ap_bot:1382718727568756857> Auracolls Voting",
            description=(
                f"- **Your last vote**: {last_vote}\n"
                f"- **Total votes**: `{total_votes}`\n"
                f"- **Rank**: `#{rank}`\n\n"
                f"Want extra rewards? Checkout </premium:1409937275927924836>"
            ),
            color=discord.Color.from_str("#ff6b6b")
        )
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        embed.set_footer(text="Global leaderboard: avotelb")

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="📥 Vote", style=discord.ButtonStyle.link, url=VOTE_LINK))

        if isinstance(ctx_or_inter, commands.Context):
            await ctx_or_inter.send(embed=embed, view=view)
        else:
            await ctx_or_inter.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Vote(bot))
