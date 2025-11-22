import discord
from discord.ext import commands, tasks
from discord import app_commands
import json, os
from datetime import datetime, timedelta

OWNER_ID = 941902212303556618 
GUILD_ID = 1327949138930700288  
PREMIUM_ROLE_ID = 1409942592660967596 
LOG_CHANNEL_ID = 1422267969253413087 

PREMIUM_FILE = "premium.json"


def load_premium():
    if not os.path.exists(PREMIUM_FILE):
        with open(PREMIUM_FILE, "w") as f:
            json.dump({"users": {}}, f)
    with open(PREMIUM_FILE, "r") as f:
        return json.load(f)


def save_premium(data):
    with open(PREMIUM_FILE, "w") as f:
        json.dump(data, f, indent=4)


def parse_duration(duration: str) -> timedelta:
    unit = duration[-1]
    value = int(duration[:-1])
    if unit == "d":
        return timedelta(days=value)
    elif unit == "y":
        return timedelta(days=value * 365)
    else:
        raise ValueError("Invalid duration format! Use d (days) or y (years).")


async def give_role(bot, user_id: int):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    role = guild.get_role(PREMIUM_ROLE_ID)
    member = guild.get_member(user_id)
    if member and role:
        await member.add_roles(role, reason="Granted Premium")


async def remove_role(bot, user_id: int):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    role = guild.get_role(PREMIUM_ROLE_ID)
    member = guild.get_member(user_id)
    if member and role and role in member.roles:
        await member.remove_roles(role, reason="Premium expired/removed")


class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_expired.start()

    def cog_unload(self):
        self.cleanup_expired.cancel()

    @tasks.loop(hours=1)
    async def cleanup_expired(self):
        data = load_premium()
        updated = False
        for uid, user_data in list(data.get("users", {}).items()):
            expiry = datetime.fromisoformat(user_data["expiry"])
            if datetime.utcnow() > expiry:
                del data["users"][uid]
                updated = True
                await remove_role(self.bot, int(uid))

                user = self.bot.get_user(int(uid))
                if user:
                    embed = discord.Embed(
                        title="<:ac_sad:1409944288522928199> AuraColls Premium Expired",
                        description=f"Your **AuraColls Premium** has ended.",
                        color=0xED4245,
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Expiry Date", value=f"<t:{int(expiry.timestamp())}:F> (<t:{int(expiry.timestamp())}:R>)", inline=False)
                    try:
                        await user.send(embed=embed)
                    except discord.Forbidden:
                        pass

                log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    log_embed = discord.Embed(
                        title="<:ac_sad:1409944288522928199> Premium Expired",
                        description=f"<@{uid}>'s premium has expired automatically.",
                        color=0xED4245,
                        timestamp=datetime.utcnow()
                    )
                    log_embed.add_field(name="User ID", value=uid)
                    await log_channel.send(embed=log_embed)

        if updated:
            save_premium(data)

    @commands.hybrid_command(name="premium", description="Get info about AuraColls Premium")
    async def premium(self, ctx: commands.Context):
        data = load_premium()
        user_data = data.get("users", {}).get(str(ctx.author.id))

        embed = discord.Embed(
            title="<:ac_premium:1412065919882235914> AuraColls Premium",
            color=discord.Color.from_str("#ff6b6b")
        )

        if user_data:
            expiry = datetime.fromisoformat(user_data["expiry"])
            embed.description = (
                f"<a:ac_yay:1409934560699093054> You are a **Premium Member**!\n"
                f"Expires on: <t:{int(expiry.timestamp())}:F> (<t:{int(expiry.timestamp())}:R>)"
            )
            embed.set_footer(text="Please don’t let your Premium expire, our journey isn’t over :c")
        else:
            embed.description = (
                "**Unlock Premium Benefits!**\n\n"
                "- No cooldown delays when trading collectibles\n"
                "- Earn 2 extra coins for every trade\n"
                "- Coinflip cooldown reduced to just 3 seconds\n"
                "- Receive 25 bonus coins on your daily claim\n"
                "- Get 100 extra coins on your weekly claim\n"
                "- Earn 10 additional coins when voting\n"
                "- Premium badge displayed in `aprofile`\n"
                "- Priority support via ticket system\n\n"
                "**How to activate Premium:**\n"
                "Open a ticket in our **[Support Server](https://discord.gg/becvfQ9fCr)**"
            )
            embed.set_footer(text="Support the bot’s development by getting Premium ❤️")

        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed)
        else:
            await ctx.reply(embed=embed, mention_author=False)

    @app_commands.command(name="addpremium", description="Grant premium to a user (Owner only)")
    @app_commands.describe(user="User to grant premium", duration="How long? e.g. 1d, 30d, 1y")
    async def add_premium(self, interaction: discord.Interaction, user: discord.User, duration: str):
        if interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("<:ac_crossmark:1399650396322005002> You are not allowed to use this command.", ephemeral=True)

        try:
            delta = parse_duration(duration)
        except ValueError:
            return await interaction.response.send_message("<:ac_crossmark:1399650396322005002> Invalid duration! Use `1d`, `30d`, or `1y`.", ephemeral=True)

        now = datetime.utcnow()
        data = load_premium()
        user_data = data.get("users", {}).get(str(user.id))

        if user_data:
            current_expiry = datetime.fromisoformat(user_data["expiry"])
            new_expiry = (current_expiry + delta) if current_expiry > now else (now + delta)
            start_time = user_data["start"]
        else:
            new_expiry = now + delta
            start_time = now.isoformat()

        data["users"][str(user.id)] = {"start": start_time, "expiry": new_expiry.isoformat()}
        save_premium(data)

        await give_role(self.bot, user.id)

        embed = discord.Embed(
            title="<a:ac_yay:1409934560699093054> AuraColls Premium Activated!",
            description=f"You have been granted **AuraColls Premium**.",
            color=0x57F287,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="New Expiry", value=f"<t:{int(new_expiry.timestamp())}:F> (<t:{int(new_expiry.timestamp())}:R>)", inline=False)
        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass

        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="<a:ac_yay:1409934560699093054> Premium Granted",
                description=f"{user.mention} has been granted premium by {interaction.user.mention}.",
                color=0x57F287,
                timestamp=datetime.utcnow()
            )
            log_embed.add_field(name="Expiry", value=f"<t:{int(new_expiry.timestamp())}:F> (<t:{int(new_expiry.timestamp())}:R>)", inline=False)
            await log_channel.send(embed=log_embed)

        await interaction.response.send_message(f"<:ac_checkmark:1399650326201499798> {user.mention} has been granted premium until <t:{int(new_expiry.timestamp())}:F>.", ephemeral=True)

    @app_commands.command(name="removepremium", description="Remove premium from a user (Owner only)")
    async def remove_premium(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("<:ac_crossmark:1399650396322005002> You are not allowed to use this command.", ephemeral=True)

        data = load_premium()
        if str(user.id) not in data.get("users", {}):
            return await interaction.response.send_message(f"{user.mention} does not have premium.", ephemeral=True)

        del data["users"][str(user.id)]
        save_premium(data)

        await remove_role(self.bot, user.id)

        embed = discord.Embed(
            title="<:ac_sad:1409944288522928199> AuraColls Premium Removed",
            description="Your **AuraColls Premium** has been removed.",
            color=0xED4245,
            timestamp=datetime.utcnow()
        )
        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass

        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="<:ac_sad:1409944288522928199> Premium Removed",
                description=f"{user.mention}'s premium has been removed by {interaction.user.mention}.",
                color=0xED4245,
                timestamp=datetime.utcnow()
            )
            await log_channel.send(embed=log_embed)

        await interaction.response.send_message(f"<:ac_checkmark:1399650326201499798> {user.mention} has been removed from premium.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Premium(bot))
