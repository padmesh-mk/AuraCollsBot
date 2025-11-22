import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json

BANS_FILE = "tempbans.json"
OWNER_ID = 941902212303556618  # replace with your ID

def load_bans():
    try:
        with open(BANS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_bans(data):
    with open(BANS_FILE, "w") as f:
        json.dump(data, f, indent=4)

class TempBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bans = load_bans()

        # Global check for ALL commands (servers + DMs)
        @bot.check
        async def block_banned(ctx):
            user_id = str(ctx.author.id)
            if user_id in self.bans:
                expiry = datetime.fromisoformat(self.bans[user_id]["expiry"])
                if datetime.utcnow() < expiry:
                    # User still banned → block without message
                    return False
                else:
                    # Ban expired, remove it
                    del self.bans[user_id]
                    save_bans(self.bans)
            return True

    # Ban command
    @commands.command(name="ban")
    async def tempban(self, ctx, user: discord.User, days: int, *, reason: str = None):
        if ctx.author.id != OWNER_ID:
            return  # silently ignore if not owner

        expiry = datetime.utcnow() + timedelta(days=days)
        reason = reason or "Violating bot rules"

        # Save with expiry + reason
        self.bans[str(user.id)] = {
            "expiry": expiry.isoformat(),
            "reason": reason
        }
        save_bans(self.bans)

        # Try to DM the banned user
        try:
            await user.send(
                f"You have been **banned** from using AuraColls!\n"
                f"**Duration:** {days} days (<t:{int(expiry.timestamp())}:F>)\n"
                f"**Reason:** {reason}\n"
                f"If this was a mistake, join our [support server](https://discord.gg/becvfQ9fCr) to appeal!"
            )
        except discord.Forbidden:
            await ctx.send(f"⚠️ Could not DM **{user.display_name}** (DMs closed).")

        await ctx.send(
            f"<:ac_checkmark:1399650326201499798> **{user.display_name}** has been banned until <t:{int(expiry.timestamp())}:R>.\n"
            f"**Reason:** {reason}"
        )

    # Unban command
    @commands.command(name="unban")
    async def unban(self, ctx, user: discord.User):
        if ctx.author.id != OWNER_ID:
            return  # silently ignore if not owner

        user_id = str(user.id)
        if user_id in self.bans:
            del self.bans[user_id]
            save_bans(self.bans)

            # Try to DM the unbanned user
            try:
                await user.send(
                    f"<:ac_checkmark:1399650326201499798> You have been **unbanned** and can now use AuraColls again."
                )
            except discord.Forbidden:
                pass

            await ctx.send(f"<:ac_checkmark:1399650326201499798> **{user.display_name}** is now unbanned.")
        else:
            await ctx.send(f"<:ac_crossmark:1399650396322005002> **{user.display_name}** is not banned.")

async def setup(bot):
    await bot.add_cog(TempBan(bot))
